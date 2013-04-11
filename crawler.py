#!/usr/bin/env python

import re
import os
import sys
import time
import math
import urllib2
import urlparse
import optparse
import hashlib
import fileinput
import shutil, errno

from tempfile import mkstemp
from shutil import move
from os import remove, close

from posixpath import basename, dirname

from cgi import escape
from traceback import format_exc
from Queue import Queue, Empty as QueueEmpty

from bs4 import BeautifulSoup
from HTMLParser import HTMLParser


__version__ = "0.2"
USAGE = "%prog [options] <url>"
VERSION = "%prog v" + __version__

AGENT = "%s/%s" % (__name__, __version__)


class Link (object):

    def __init__(self, src, dst, link_type):
        self.src = src
        self.dst = dst
        self.link_type = link_type

    """
    NOTE: If your class is intended to be subclassed, and you have attributes that 
    you do not want subclasses to use, consider naming them with double leading 
    underscores and no trailing underscores. This invokes Python's name mangling 
    algorithm, where the name of the class is mangled into the attribute name. 
    This helps avoid attribute name collisions should subclasses inadvertently 
    contain attributes with the same name.
    """
    def __hash__(self):
        return hash((self.src, self.dst, self.link_type))

    def __eq__(self, other):
        return (self.src == other.src and
                self.dst == other.dst and
                self.link_type == other.link_type)
    
    def __str__(self):
        return self.src + " -> " + self.dst

class Crawler(object):

    """
    The Crawler repeatedly searches an HTML parse tree starting from the supplied URL.
    """

    def __init__(self, root, depth_limit, confine=None, exclude=[], locked=True, filter_seen=True):
        self.root = root
        self.host = urlparse.urlparse(root)[1]

        ## Data for filters:
        self.depth_limit = depth_limit # Max depth (number of hops from root)
        self.locked = locked           # Limit search to a single host
        self.confine_prefix=confine    # Limit search to this prefix
        self.exclude_prefixes=exclude; # URL prefixes NOT to visit
                
        self.urls_seen = set()          # Used to avoid putting duplicates in queue
        self.urls_remembered = set()    # Used for reporting to user
        self.visited_links= set()       # Used to avoid re-processing a page
        self.links_remembered = set()   # Used for reporting to user
        
        self.num_links = 0              # Links found (and not excluded by filters)
        self.num_followed = 0           # Links followed.  

        # Pre-visit filters:  Only visit a URL if it passes these tests
        self.pre_visit_filters=[self._prefix_ok,
                                self._exclude_ok,
                                self._not_visited,
                                self._same_host]

        # Out-url filters: When examining a visited page, only process
        # links where the target matches these filters.        
        if filter_seen:
            self.out_url_filters=[self._prefix_ok, 
                                  self._same_host]
        else:
            self.out_url_filters=[]

    def _pre_visit_url_condense(self, url):
        
        """All this does is strip the \"fragment\" component from URLs,
        so that http://plu.edu/csce499.html\#csce499 becomes
        http://plu.edu/csce499.html """

        base, frag = urlparse.urldefrag(url)
        return base

    """
    ## URL Filtering functions: 
    ## These all use information from the state of the Crawler to evaluate 
    ## whether a given URL should be used in some context.  Return value 
    ## of True indicates that the URL should be used.
    """
    
    def _prefix_ok(self, url):
        """Pass if the URL has the correct prefix, or none is specified"""
        return (self.confine_prefix is None  or
                url.startswith(self.confine_prefix))

    def _exclude_ok(self, url):
        """Pass if the URL does not match any exclude patterns"""
        prefixes_ok = [ not url.startswith(p) for p in self.exclude_prefixes]
        return all(prefixes_ok)
    
    def _not_visited(self, url):
        """Pass if the URL has not already been visited"""
        return (url not in self.visited_links)
    
    def _same_host(self, url):
        """Pass if the URL is on the same host as the root URL"""
        try:
            host = urlparse.urlparse(url)[1]
            return re.match(".*%s" % self.host, host) 
        except Exception, e:
            print >> sys.stderr, "ERROR: Can't process url '%s' (%s)" % (url, e)
            return False
            

    def crawl(self):

        """ 
        The Crawler component  repeatedly searches the HTML parse tree for <A> tags. To be 
        added to the search queue, the <A> tag must meet the following conditions:

        1) The URL must be within the specific depth limit provided by the user.
        2) The URL must be new and one that hasn't been visited by the crawl queue previously.
        3) The URL must not match any of the "do not follow" filters defined by the user. 

        The Crawler will continue to execute until all URL's in the siteparse tree have 
        been visited and searched for additional URL's. Once this has completed the Crawler will exit.
        """
        
        q = Queue()
        q.put((self.root, 0))

        while not q.empty():
            this_url, depth = q.get()
            
            #Non-URL-specific filter: Discard anything over depth limit
            if depth > self.depth_limit:
                continue
            
            #Apply URL-based filters.
            do_not_follow = [f for f in self.pre_visit_filters if not f(this_url)]
            
            #Special-case depth 0 (starting URL)
            if depth == 0 and [] != do_not_follow:
                print >> sys.stderr, "Whoops! Starting URL %s rejected by the following filters:", do_not_follow

            #If no filters failed, process URL
            if [] == do_not_follow:
                try:
                    self.visited_links.add(this_url)
                    self.num_followed += 1
                    page = Fetcher(this_url)
                    page.fetch()
                    for link_url in [self._pre_visit_url_condense(l) for l in page.out_links()]:
                        if link_url not in self.urls_seen:
                            q.put((link_url, depth+1))
                            self.urls_seen.add(link_url)
                            
                        do_not_remember = [f for f in self.out_url_filters if not f(link_url)]
                        if [] == do_not_remember:
                                self.num_links += 1
                                self.urls_remembered.add(link_url)
                                link = Link(this_url, link_url, "href")
                                if link not in self.links_remembered:
                                    self.links_remembered.add(link)
                except Exception, e:
                    print >>sys.stderr, "ERROR: Can't process URL '%s' (%s)" % (this_url, e)
                    #print format_exc()

class OpaqueDataTypeException (Exception):
    
    """
    Opaque Data type is a data type that is incompletely defined in an 
    interface, so that its values can only be manipulated by calling 
    subroutines that have access to the missing information. The concrete 
    representation of the type is hidden from its users. (WIKIPEDIA)
    """

    def __init__(self, message, mimetype, url):

        Exception.__init__(self, message)
        self.mimetype=mimetype #Multi-Purpose Intenet Mail Extensions 
        self.url=url
        

class Fetcher(object):
    
    """
    The Fetcher class is used to retrieve and interpretting web pages
    using the BeautifulSoup library for screen-scraping HTML. 
    """

    def __init__(self, url):
        self.url = url
        self.out_urls = []

    def __getitem__(self, x):
        return self.out_urls[x]

    def out_links(self):
        return self.out_urls

    def _addHeaders(self, request):
        request.add_header("User-Agent", AGENT)

    def _open(self):
        url = self.url
        try:
            request = urllib2.Request(url)
            handle = urllib2.build_opener()
        except IOError:
            return None
        return (request, handle)

    def fetch(self):
        request, handle = self._open()
        self._addHeaders(request)
        if handle:
            try:
                data=handle.open(request)
                mime_type=data.info().gettype()
                url=data.geturl();
                if mime_type != "text/html":
                    raise OpaqueDataTypeException("Not interested in files of type %s" % mime_type,
                                              mime_type, url)
                content = unicode(data.read(), "utf-8",
                        errors="replace")
                soup = BeautifulSoup(content)
                tags = soup('a') # Scrape 'a' from HREF using BeautufulSoup object
            except urllib2.HTTPError, error:
                if error.code == 404:
                    print >> sys.stderr, "ERROR: %s -> %s" % (error, error.url)
                else:
                    print >> sys.stderr, "ERROR: %s" % error
                tags = []
            except urllib2.URLError, error:
                print >> sys.stderr, "ERROR: %s" % error
                tags = []
            except OpaqueDataTypeException, error:
                print >>sys.stderr, "Skipping %s, has type %s" % (error.url, error.mimetype)
                tags = []
            for tag in tags:
                href = tag.get("href")
                pattern = '()@;'
                if href is not None:
                    url = urlparse.urljoin(self.url, escape(href))
                    if url not in self:
                        if url[-1:] != '/':
                            #Omit URL's that are email or other none pages
                            r = re.compile('[()@]')
                            if not r.search(url):
                                self.out_urls.append(url)
                    print url

                    scraper = Scraper()
                    scraper.scrapePage(content, url) #Scrape page for specific HTML elements



class Generate(object):

    def __init__(self):
        self

    def copyAnything(self, src, dst):
        try:
            shutil.copytree(src, dst)
        except OSError as exc: # python >2.5
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else: raise

    def generateFramework(self):

        dir_framework = dest_dir
        
        #Erase previous generation
        if os.path.isdir(dir_framework):
            shutil.rmtree(dir_framework)

        os.mkdir(dir_framework)
        os.mkdir(dir_framework + "/browserid")
        os.mkdir(dir_framework + "/docs")
        os.mkdir(dir_framework + "/pages")
        os.mkdir(dir_framework + "/tests")
        os.mkdir(dir_framework + "/utils")
        os.mkdir(dir_framework + "/pages/auto")
        os.mkdir(dir_framework + "/tests/auto")           

    def generateVariable(self, fh, var, define):

        if var is '_page_title': 
           fh.write("\n    " + var + " = \"" + define + "\"")
        else:
           fh.write("\n    " + var + " = " + define)


    def generateFindElement(self, fh, var):

        wc1 = "{{WILDCARD1}}"
        wc2 = "{{WILDCARD2}}"

        lib_page_is_element_visible = "lib/page_is_element_visible.py"

        content = open(lib_page_is_element_visible).read()
        replacedText = content.replace(wc1, var)
        replacedText = replacedText.replace(wc2, var)

        fh.write("\n" + replacedText)

#    """

#    """
#    def generateVerifyElement():
#        return

#    """

    def generateTestElement(self, classname, filetext, testMethods):

        filename = "test_" + classname.lower() + ".py"
        outputFile = dest_dir + "/tests/auto/" + filename
        fh = open(outputFile, "w")

        fh.write("#!/usr/bin/env python")
        fh.write("\n")

        # Added to handle py.test error exception related to Python path
        #fh.write("import sys, os\n")
        #fh.write("myPath = os.path.dirname(os.path.abspath(__file__))\n")
        #fh.write("sys.path.insert(0, myPath + '/usr/share/python/')\n")

        fh.write("import pytest\n")
        fh.write("from unittestzero import Assert\n")
        fh.write("from pages.auto." + classname.lower() + " import " + classname + "\n")
        #fh.write("from pages." + filetext.lower() + " import " + classname + "\n")

        #fh.write("\nclass HeaderMenu:\n")
        #fh.write("\n")

        #lib_test_element_header = "lib/test_element_header.py"
        #defaultDef = open(lib_test_element_header).read()
        #fh.write(defaultDef + "\n")

        fh.write("class Test" + classname + ":\n")
        
        #CLIFF NOTE: Add Page Title Test

        for test in testMethods:
            fh.write("\n    @pytest.mark.nondestructive\n")
            fh.write("    def test_" + test + "(self, mozwebqa):\n")
            fh.write("\n")
            fh.write("        page = " + classname + "(mozwebqa)\n")
            fh.write("        Assert.true(page." + test + ")\n")
            
        #GOTIME
        return


class Scraper(object):
    
    """
    The Scraper class is used to scrape a visited page for specific HTML elements. The 
    following is a list of all HTML elements that are scraped from the page:

       1) Page Title
       2) All DIV's with ID tag
       3) H1 Text
       4) Image Files
       5) Radio Buttons
       6) Checkboxes
       7) Text Fields
       8) Password Text Fields
       9) Buttons

    Please review the Design Document regarding the specific HTML elements parsed and naming convention.
    """

    def __init__(self):
        self

    """
    Method used to remote HTML tags. 
    Call using the following example syntax: removeTags(testhtml, 'b', 'p')
    """
    def removeTags(html, *tags):
        soup = BeautifulSoup(html)
        for tag in tags:
            for tag in soup.findAll(tag):
                tag.replaceWith("")

        return soup


    def scrapePage(self, content, url):
        
        soup = BeautifulSoup(content)

        parse_object = urlparse.urlparse(url)
        filepath = parse_object.path[1:]

        filepath = filepath.replace ("/", "_")
        filepath = filepath.replace (".", "_")
        filepath = filepath.replace ("-", "_")
        filepath = filepath.rstrip('_')

        #Create Class Name
        classname = filepath.title()
        scraper = Scraper()

        #Do not create for NULL string
        if classname != "":
            pattern = re.compile(r'\d\@\?\=,') #Search for email address characters
            if pattern.findall(classname):
                print 'Found'
            else:
                print 'Not found'
                scraper.scrapePageCont(content, url, classname, filepath)


    def scrapePageCont(self, content, url, classname, filepath):

        soup = BeautifulSoup(content)
        testMethods = []


        #Class name cannot start with digit.  
        m = classname[0].isdigit()
        if m:
            classname = "c" + classname
            filepath = "c" + filepath

        filetext = classname
        classname = classname.replace ("_", "")
        filename = dest_dir + "/pages/auto/" + classname.lower() + ".py"
        #filename = dest_dir + "/pages/" + filepath.lower() + ".py"
        
        #Create new page object file using file name Class Name
        fh = open(filename, "w")
        print"\nURL - " + filepath
        print"\nFILEPATH - " + classname 
        fh.write("#!/usr/bin/env python")
        ph = open("lib/page_header.py", "r")
        fh.write("\n\n" + ph.read())
        ph.close()
        fh.write("\n\nclass " + classname + "(Base):\n") 
        

        """
        Parse Title:
           (a) HTML Syntax: <title>CSCE 499 - Design Document</title>
           (b) BeautifulSoup Syntax: print soup.head.title
           (c) Variable Definition: _page_title = "CSCE 499 - Design Document"
           (d) Generated Selenium: The generated code should verify that the title string matches the ex-
               pected text as defined by the title variable.

        """
        print "\nPARSE PAGE TITLE"
        fh.write("\n\n    # Page Title Variable")
        title = soup.head.title.string 
        gen = Generate()
        gen.generateVariable(fh, "_page_title", title)
        print title

        """
        All DIV with ID tag
           (a) HTML Syntax: <div id="banner-top">
           (b) BeautifulSoup Syntax: divs = soup.findAll('div','id':True)
           (c) Variable Definition: _div_banner_top_locator = (By.ID, "banner-top")
           (d) Generated Selenium: The generated code should verify that the DIV ID exists on the page.
        """
        print "\nPARSE ALL DIVS WITH IDS" #CLIFF NOTE: Possibly delete or add debug condition for printing.

        fh.write("\n\n    # Variables defined by ID element")
        divs = soup.findAll('div',{'id':True})    
        for div in divs:
            #print div
	    d = div['id']
            print d 
            print d.replace ("-", "_") #CLIFF NOTE: Use this when manipulating string syntax for Selenium

            varName = "_id_" + d.replace("-", "_") + "_locator"
            byIdSyntax = "(By.ID, \""+ d + "\")"
            gen.generateVariable(fh, varName, byIdSyntax)
        


        """
        H1 Text
           (a) HTML Syntax: <h1>CSCE 499 Capstone - 2012-2013</h1>
           (b) BeautifulSoup Syntax: h1s = soup.findAll('h1')
           (c) Variable Definition: _h1_CSCE_499_Capstone = "CSCE 499 Capstone - 2012-2013"
           (d) Generated Selenium: The generated code should verify that the H1 text exists and matches
               the expected text as defined by the specific H1 variable.
        """
        print "\nPARSE H1" #CLIFF NOTE: Possibly delete or add debug condition for printing.
        h1s = soup.findAll('h1')    
        for h1 in h1s:
	    print h1

        """
        Image Files
           (a) HTML Syntax: <img src="/home-assets/images/banner-images/honors.jpg" alt="" border="0">
           (b) BeautifulSoup Syntax: imgs = soup.findAll('img')
           (c) Variable Definition: _img_honors_locator = (By.SRC, "/home-assets/images/banner-images/honors
           (d) Generated Selenium: The generat

        """
        print "\nPARSE IMG" #CLIFF NOTE: Possibly delete or add debug condition for printing.
        imgs = soup.findAll('img')    
        for img in imgs:
	    print img

        """
        CLIFF NOTE: Re-investigate this one to see if it is really needed for testing
        """
        print "\nPARSE IFRAMES" #CLIFF NOTE: Possibly delete or add debug condition for printing.
        iframes = soup.findAll('iframe')    
        for iframe in iframes:
	    print iframe.extract()

        """
        Radio Buttons
           (a) HTML Syntax: <input type="radio" name="group1" value="Cheese">
           (b) BeautifulSoup Syntax: radios = soup.findAll('input','type':'radio')
           (c) Variable Definition: _radio_cheese_locator = (By.Value, "Cheese")
           (d) Generated Selenium: The generated code should verify that the radio button exists, is selectable
               and simulates the "click" action in a basic sanity test.
        """
        print "\nPARSE RADIO BUTTONS" #CLIFF NOTE: Possibly delete or add debug condition for printing.
        radios = soup.findAll('input',{'type':'radio'})
        for radio in radios:
	    print radio

        """
        Checkboxes
           (a) HTML Syntax: <input type="checkbox" name="sports" value="football">
           (b) BeautifulSoup Syntax: checkboxes = soup.findAll('input','type':'checkbox')
           (c) Variable Definition: _checkbox_sports_locator = (By.Value, "football")
           (d) Generated Selenium: The generated code should verify that the check box exists, is selectable
               and simulates the "click" action in a basic sanity test.
        """
        print "\nPARSE CHECKBOX BUTTONS" #CLIFF NOTE: Possibly delete or add debug condition for printing.
        checkboxes = soup.findAll('input',{'type':'checkbox'})
        for checkbox in checkboxes:
	    print checkbox

        """
        Text Fields
           (a) HTML Syntax: <textarea name="comments" cols="25" rows="5">Enter your comments here...
               </textarea>
           (b) BeautifulSoup Syntax: textboxes = soup.findAll('input','type':'text')
           (c) Variable Definition: _text_comments_locator = (By.Name, "comments")
           (d) Generated Selenium: The generated code should verify that the text area exists, is accessible
               by typing sample text and does not fail any SQL Injection negative test cases.
        """
        print "\nPARSE TEXT BOXES" #CLIFF NOTE: Possibly delete or add debug condition for printing.
        #CLIFF NOTE: <input class="search-string swaptext" name="q" type="text" value="SEARCH PLU"/>
        textboxes = soup.findAll('input',{'type':'text'})
        for textbox in textboxes:

            print textbox

            text_id = textbox.get('id')
            text_class = textbox.get('class')

            if text_id != "" and text_class != "" :
                out_str = ""
                for tc in text_class:
                    out_str += tc + "."
                
                if out_str[-1:] == '.':
                    out_str = out_str[:-1]

                #Print Class
                print out_str

                out_str2 = out_str.replace("-", "_")
                out_str2 = out_str2.replace(".", "_")
                varTextboxClass = "_textbox_class_" + out_str2 + "_locator"
                byCssSelectorSyntax = "(By.CSS_Selector, \""+ out_str + "\")"
                gen.generateVariable(fh, varTextboxClass, byCssSelectorSyntax)
                fh.write("\n")
                gen.generateFindElement(fh, varTextboxClass)

            if text_id  != "" and text_class == "":
                print text_id
                varTextboxId = "_textbox_id_" + out_str.replace("-", "_") + "_locator"
                byIdSyntax = "(By.ID, \""+ d + "\")"
                gen.generateVariable(fh, varTextboxId, byIdSyntax)
                fh.write("\n")
                gen.generateFindElement(fh, varTextboxId)


            if text_id == "" and text_class  != "":
                out_str = ""
                for tc in text_class:
                    out_str += tc + "."
                
                if out_str[-1:] == '.':
                    out_str = out_str[:-1]

                #Print Class
                print out_str
                out_str2 = out_str.replace("-", "_")
                out_str2 = out_str2.replace(".", "_")
                varTextboxClass = "_textbox_class_" + out_str2 + "_locator"
                byCssSelectorSyntax = "(By.CSS_Selector, \""+ out_str + "\")"
                gen.generateVariable(fh, varTextboxClass, byCssSelectorSyntax)
                fh.write("\n")                
                gen.generateFindElement(fh, varTextboxClass)


            #varName = "_id_" + d.replace("-", "_") + "_locator"
            #byIdSyntax = "(By.ID, \""+ d + "\")"
            #gen.generateVariable(fh, varName, byIdSyntax)
           

        """
        Password Text Fields
           (a) HTML Syntax: <input type="password" size="25">
           (b) BeautifulSoup Syntax: passwords = soup.findAll('input','type':'password')
           (c) Variable Definition: _text_password_locator = (By.Type, "password")
           (d) Generated Selenium: The generated code should verify that the password text area exists, is
               accessible by typing hidden characters and does not fail any negative test case scenarios (e.g., SQL
               Injections and Security Tests).
        """
        print "\nPARSE TEXT BOXES" #CLIFF NOTE: Possibly delete or add debug condition for printing.
        passwords = soup.findAll('input',{'type':'password'})
        for password in passwords:
	    print password
    
        """
        Buttons
           (a) HTML Syntax: <input type="submit" value="Submit">
           (b) BeautifulSoup Syntax: button = soup.findAll('input','type':'submit')
           (c) Variable Definition: _button_submit_locator = (By.Type, "submit")
           (d) Generated Selenium: The generated code should verify that the button exists, is able to be
               clicked and functions correctly when selected.
        """
        print "\nPARSE BUTTONS" #CLIFF NOTE: Possibly delete or add debug condition for printing.
        buttons = soup.findAll('input',{'type':'submit'})
        for button in buttons:
	    print button


        #Extract base name for url
        o = urlparse.urlparse(url)
        bname = basename(o.path)
        print"\nBASE NAME = " + bname

        #Creates a new instance of the class and gets the page ready for testing
        wc4 = "{{WILDCARD4}}"
        page_init = "lib/page_init.py"
        ph = open(page_init).read()
        initialize = ph.replace(wc4, bname)
        fh.write("\n\n" + initialize)


        """
        Generate DIV Find Element Methods
        """
        fh.write("\n")

        for div in divs:
	    d = div['id']
            print d 
            print d.replace ("-", "_") #CLIFF NOTE: Use this when manipulating string syntax for Selenium

            varName = "_id_" + d.replace("-", "_") + "_locator"
            
            methodName = "is" + varName + "_available"
            testMethods.append(methodName)
            gen.generateFindElement(fh, varName)

        fh.close()
       
        print "TEST METHODS"
        print testMethods
        if classname != "":
            gen.generateTestElement(classname, filetext, testMethods)    


def getLinks(url):

    page = Fetcher(url)
    page.fetch()
    for i, url in enumerate(page):
        print "%d. %s" % (i, url)


def parse_options():
       
    """
    Parse any command-line options given returning both
    the parsed options and arguments.
    """

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-q", "--quiet",
                      action="store_true", default=False, dest="quiet",
                      help="Enable quiet mode")

    parser.add_option("-l", "--links",
                      action="store_true", default=False, dest="links",
                      help="Get links for specified url only")    

    parser.add_option("-d", "--depth",
                      action="store", type="int", default=30, dest="depth_limit",
                      help="Maximum depth to Crawl")

    parser.add_option("-c", "--confine",
                      action="store", type="string", dest="confine",
                      help="Confine crawl to specified prefix")

    parser.add_option("-x", "--exclude", action="append", type="string",
                      dest="exclude", default=[], help="Exclude URLs by prefix")
   
    parser.add_option("-L", "--show-links", action="store_true", default=False,
                      dest="out_links", help="Output links found")

    parser.add_option("-u", "--show-urls", action="store_true", default=False,
                      dest="out_urls", help="Output URLs found")
    
    parser.add_option("-o", "--output", action="store", type="string", default="SeleniumAuto",
                      dest="output", help="Output Directory to Generate To")


    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help(sys.stderr)
        raise SystemExit, 1

    if opts.out_links and opts.out_urls:
        parser.print_help(sys.stderr)
        parser.error("Mutually exclusive options: -L and -u")

    return opts, args


def main():    

    opts, args = parse_options()
    url = args[0]

    if opts.links:
        getLinks(url)
        raise SystemExit, 0

    depth_limit = opts.depth_limit
    confine_prefix=opts.confine
    exclude=opts.exclude

    sTime = time.time()

    global dest_dir # Output folder used throughout...
    dest_dir = opts.output

    gen = Generate()
    gen.generateFramework()
    
    #Copy all prerequisite files
    src1 = "conftest.py"
    src2 = "credentials.yaml"
    src3 = "mozwebqa.cfg"
    src4 = "README.md"
    src5 = "requirements.txt"
    src6 = "page.py"
    src7 = "__init__.py"
    src8 = "base.py"

    gen.copyAnything("lib/" + src1, dest_dir + "/" + src1)
    gen.copyAnything("lib/" + src2, dest_dir + "/" + src2)
    gen.copyAnything("lib/" + src3, dest_dir + "/" + src3)
    gen.copyAnything("lib/" + src4, dest_dir + "/" + src4)
    gen.copyAnything("lib/" + src5, dest_dir + "/" + src5)

    wc3 = "{{WILDCARD3}}"
    mozwebqaInput = "lib/mozwebqa.cfg"
    mozwebqaOutput = dest_dir + "/" + src3

    fh1 = open(mozwebqaInput).read()
    mozwebqa = fh1.replace(wc3, url)
    fh2 = open(mozwebqaOutput, "w")
    fh2.write(mozwebqa)
    fh2.close()

    gen.copyAnything("lib/" + src6, dest_dir + "/pages/" + src6)
    gen.copyAnything("lib/" + src7, dest_dir + "/pages/" + src7)

    gen.copyAnything("lib/" + src7, dest_dir + "/tests/" + src7)
    gen.copyAnything("lib/" + src7, dest_dir + "/tests/auto/" + src7)
    gen.copyAnything("lib/" + src8, dest_dir + "/pages/auto/" + src8)
    gen.copyAnything("lib/" + src7, dest_dir + "/pages/auto/" + src7)

    print >> sys.stderr,  "Crawling %s (Max Depth: %d)" % (url, depth_limit)
    crawler = Crawler(url, depth_limit, confine_prefix, exclude)
    crawler.crawl()

    if opts.out_urls:
        print "\n".join(crawler.urls_seen)

    if opts.out_links:
        print "\n".join([str(l) for l in crawler.links_remembered])
        
    #if opts.out_dot:
    #    d = DotWriter()
    #    d.asDot(crawler.links_remembered)

    eTime = time.time()
    tTime = eTime - sTime

    print >> sys.stderr, "Found:    %d" % crawler.num_links
    print >> sys.stderr, "Followed: %d" % crawler.num_followed
    print >> sys.stderr, "Stats:    (%d/s after %0.2fs)" % (
            int(math.ceil(float(crawler.num_links) / tTime)), tTime)

if __name__ == "__main__":
    main()
