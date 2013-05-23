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
import datetime
import logging

from tempfile import mkstemp
from shutil import move
from os import remove, close
from posixpath import basename, dirname
from cgi import escape
from traceback import format_exc
from Queue import Queue, Empty as QueueEmpty

from bs4 import BeautifulSoup
from HTMLParser import HTMLParser

"""
TITLE: 
Automated Generation of Test Code for Web Applications

ABSTRACT:
Developing a test automation framework for a website requires many man-hours 
of development time. By leveraging several popular open source test tools, 
site crawling and element scraping techniques, this project automates the 
generation of test code for a web application in a matter of minutes.
"""

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

    def _open(self):
        url = self.url
        try:
            request = urllib2.Request(url)
            handle = urllib2.build_opener()
        except IOError:
            return None
        return (request, handle)

    def output_links(self):
        return self.out_urls


    def fetch(self):

        """
        The fetch def uses BeautifulSoup and urllib2 to parse URL's for 
        additional A HREF's and call the scraper to get page elements.
        """
        request, handle = self._open()

        if handle:
            try:
                data=handle.open(request)
                url=data.geturl();
                code_syntax = unicode(data.read(), "utf-8", errors="replace")
                soup = BeautifulSoup(code_syntax)
                tags = soup('a') # Scrape 'a' from HREF using BeautufulSoup object

            except urllib2.HTTPError, error:
                if error.code == 404:
                    print >> sys.stderr, "ERROR: %s -> %s" % (error, error.url)
                    logging.error('Error Code = 404')
                else:
                    print >> sys.stderr, "ERROR: %s" % error
                    logging.error('HTTP Error found')
                tags = []

            except urllib2.URLError, error:
                print >> sys.stderr, "ERROR: %s" % error
                logging.error('URL Error found')
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
                    logging.info(url)
                    scraper = Scraper()
                    scraper.scrapePage(code_syntax, url) #Scrape page for specific HTML elements


class Spider(object):

    """
    The Spider repeatedly searches an HTML parse tree starting from the supplied URL.
    """

    def __init__(self, base_url, depth_max, restrict=None, locked=True, filter_seen=True):

        """
        Constructor
        """
        self.base_url = base_url
        self.host = urlparse.urlparse(base_url)[1]

        #Keep track of URL's visited to avoid duplication
        self.urls_viewed = set()
        self.urls_cached = set()
        self.visited_links= set()
        self.links_remembered = set()

        #Counters        
        self.count_links = 0
        self.count_followed = 0 

        #Filters data variables
        self.depth_max = depth_max
        self.locked = locked
        self.restrict_prefix=restrict
        
        # Filters must past gateway conditions
        logging.debug('Filters Gateway Definition')
        self.filters_gateway=[self._prefix_pass, self._not_visited, self._same_host]
       
        if filter_seen:
            self.out_url_filters=[self._prefix_pass, 
                                  self._same_host]
        else:
            self.out_url_filters=[]

    def _pre_visit_url_condense(self, url):

        """
        Strips the fragment component from URL's
        """
        base, frag = urlparse.urldefrag(url)
        return base

    """
    URL Filtering functions: 
    These all use information from the state of the Spider to evaluate 
    whether a given URL should be used in some context.  Return value 
    of True indicates that the URL should be used.
    """

    def _same_host(self, url):
        """
        Pass the same host as the base URL
        """
        logging.debug('URL is on the same host as the base URL')
        try:
            host = urlparse.urlparse(url)[1]
            logging.debug('HOST: ' + host)
            logging.debug('HOST (self): ' + self.host)
            return re.match(".*%s" % self.host, host) 
        except Exception, e:
            print >> sys.stderr, "ERROR: Can't process url '%s' (%s)" % (url, e)
            return False
 
    
    def _prefix_pass(self, url):
        """
        Pass if URL uses correct prefix
        """
        logging.debug('Verify tht URL has correct prefix')
        return (self.restrict_prefix is None  or
                url.startswith(self.restrict_prefix))

    def _not_visited(self, url):
        """
        Pass for URL not previously visited
        """
        logging.debug('URL has not been visited')
        return (url not in self.visited_links)
    

    def crawl(self):

        """ 
        The Spider component  repeatedly searches the HTML parse tree for <A> tags. To be 
        added to the search queue, the <A> tag must meet the following conditions:

        1) The URL must be within the specific depth limit provided by the user.
        2) The URL must be new and one that hasn't been visited by the crawl queue previously.
        3) The URL must not match any of the "do not follow" filters defined by the user. 

        The Spider will continue to execute until all URL's in the siteparse tree have 
        been visited and searched for additional URL's. Once this has completed the Spider will exit.
        """
        
        queue = Queue()
        queue.put((self.base_url, 0))

        while not queue.empty():
            url_current, depth = queue.get()
            
            if depth > self.depth_max:
                continue

            logging.debug('Pre Dont Follow')
            dont_follow = [f for f in self.filters_gateway if not f(url_current)]
            logging.debug('Post Dont Follow')

            if [] != dont_follow and depth == 0:
                print >> sys.stderr, "URL %s rejected:", dont_follow

            #Process URL
            if [] == dont_follow:
                try:
                    self.visited_links.add(url_current)
                    self.count_followed += 1
                    logging.debug('Fetching URL:' + url_current)
                    page = Fetcher(url_current)
                    page.fetch()

                    for link_url in [self._pre_visit_url_condense(l) for l in page.output_links()]:
                        if link_url not in self.urls_viewed:
                            queue.put((link_url, depth+1))
                            self.urls_viewed.add(link_url)
                            
                        do_not_remember = [f for f in self.out_url_filters if not f(link_url)]
                        if [] == do_not_remember:
                                self.count_links += 1
                                self.urls_cached.add(link_url)
                                link = Hyperlink(url_current, link_url, "href")
                                if link not in self.links_remembered:
                                    self.links_remembered.add(link)

                except Exception, e:
                    print >>sys.stderr, "ERROR: Cannot process URL '%s' (%s)" % (url_current, e)
        

class Hyperlink(object):

    def __init__(self, src, dst, type_of_link):

        """
        Constructor
        """
        self.src = src
        self.dst = dst
        self.type_of_link = type_of_link

    """
    NOTE: If your class is intended to be subclassed, and you have attributes that 
    you do not want subclasses to use, consider naming them with double leading 
    underscores and no trailing underscores. 
    """
    def __str__(self):
        return self.src + " -> " + self.dst

    def __eq__(self, other):
        return (self.src == other.src and
                self.dst == other.dst and
                self.type_of_link == other.type_of_link)

    def __hash__(self):
        return hash((self.src, self.dst, self.type_of_link))


class Generate(object):

    """
    CLIFF NOTE: ADD FUNCTION COMMENT HERE
    """

    def __init__(self):
        """
        Constructor
        """
        self

    def copyAnything(self, src, dst):
        """
        CLIFF NOTE: ADD FUNCTION COMMENT HERE
        """
        try:
            shutil.copytree(src, dst)
        except OSError as exc: # python >2.5
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else: raise

    def generateFramework(self):

        """
        CLIFF NOTE: ADD FUNCTION COMMENT HERE
        """
        dir_framework = dest_dir
        
        #Erase previous generation
        if os.path.isdir(dir_framework):
            shutil.rmtree(dir_framework)

        logging.debug('Create subdirectories for new framework')
        os.mkdir(dir_framework)
        os.mkdir(dir_framework + "/browserid")
        os.mkdir(dir_framework + "/docs")
        os.mkdir(dir_framework + "/pages")
        os.mkdir(dir_framework + "/tests")
        os.mkdir(dir_framework + "/utils")
        os.mkdir(dir_framework + "/pages/auto")
        os.mkdir(dir_framework + "/tests/auto")           


    def generateVariable(self, fh, var, define):

        """
        CLIFF NOTE: ADD FUNCTION COMMENT HERE
        """
        logging.debug('Generate variable definition:' + var)
        if var is '_page_title': 
           fh.write("\n    " + var + " = \"" + define + "\"")
        else:
           fh.write("\n    " + var + " = " + define)


    def generateFindElement(self, fh, var):

        """
        CLIFF NOTE: ADD FUNCTION COMMENT HERE
        """
        logging.debug('Generate FindElement:' + var)
        wc1 = "{{WILDCARD1}}"
        wc2 = "{{WILDCARD2}}"

        lib_page_is_element_visible = "lib/page_is_element_visible.py"

        code_syntax = open(lib_page_is_element_visible).read()
        replacedText = code_syntax.replace(wc1, var)
        replacedText = replacedText.replace(wc2, var)

        fh.write("\n" + replacedText)

#    """

#    """
#    def generateVerifyElement():
#        return

#    """

    def generateTestElement(self, classname, filetext, testMethods):

        """
        CLIFF NOTE: ADD FUNCTION COMMENT HERE
        """
        now = datetime.datetime.now()
        logging.debug('Generating ' + classname + ' test script.')
        filename = "test_" + classname.lower() + ".py"
        outputFile = dest_dir + "/tests/auto/" + filename
        fh = open(outputFile, "w")

        fh.write("#!/usr/bin/env python")
        fh.write("\n")

        fh.write("\"\"\"")
        fh.write("\nCreated on " + now.strftime("%Y-%m-%d %H:%M"))
        fh.write("\n@author: Selenium Webdriver Code Generator\n")
        fh.write("\"\"\"\n")

        fh.write("import pytest\n")
        fh.write("from unittestzero import Assert\n")
        fh.write("from pages.auto." + classname.lower() + " import " + classname + "\n")

        fh.write("class Test" + classname + ":\n")
        
        #CLIFF NOTE: Add Page Title Test

        #Create PyTest Test Case for all defined tests
        for test in testMethods:
            logging.debug('Generating test case: test_' + test)
            fh.write("\n    @pytest.mark.nondestructive\n")
            fh.write("    def test_" + test + "(self, mozwebqa):\n")
            fh.write("\n")
            fh.write("        \"\"\"\n")
            fh.write("        Test pages elements defined in " + classname + "page object: " + classname.lower() + ".py\n") 
            fh.write("        \"\"\"\n")
            fh.write("        page = " + classname + "(mozwebqa)\n")
            fh.write("        Assert.true(page." + test + ")\n")
            
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

        """
        Constructor
        """
        self


    def removeTags(html, *tags):

        """
        Method used to remote HTML tags. 
        Call using the following example syntax: removeTags(testhtml, 'b', 'p')
        """
        logging.debug('Remove remote HTML tags')
        soup = BeautifulSoup(html)
        for tag in tags:
            for tag in soup.findAll(tag):
                tag.replaceWith("")

        return soup


    def scrapePage(self, code_syntax, url):

        """
        CLIFF NOTE: ADD FUNCTION COMMENT HERE
        """
        soup = BeautifulSoup(code_syntax)

        parse_object = urlparse.urlparse(url)
        filepath = parse_object.path[1:]

        filepath = filepath.replace ("/", "_")
        filepath = filepath.replace (".", "_")
        filepath = filepath.replace ("-", "_")
        filepath = filepath.rstrip('_')

        #Create Class Name
        classname = filepath.title()
        logging.debug('Create class name ' + classname)
        scraper = Scraper()

        #Do not create for NULL string
        if classname != "":
            pattern = re.compile(r'\d\@\?\=,') #Search for email address characters
            if pattern.findall(classname):
                logging.debug(classname + 'Found')
            else:
                logging.debug(classname + 'Not Found')
                scraper.scrapePageCont(code_syntax, url, classname, filepath)


    def scrapePageCont(self, code_syntax, url, classname, filepath):

        """
        CLIFF NOTE: ADD FUNCTION COMMENT HERE
        """
        logging.debug('Scraping page')
        soup = BeautifulSoup(code_syntax)
        now = datetime.datetime.now()
        testMethods = []

        #Class name cannot start with digit.  
        m = classname[0].isdigit()
        if m:
            logging.debug('Class name cannot start with a digit')
            classname = "c" + classname
            filepath = "c" + filepath

        #Define variable for page object file name
        filetext = classname
        classname = classname.replace ("_", "")
        filename = dest_dir + "/pages/auto/" + classname.lower() + ".py"
        
        #Create new page object file using file name Class Name
        fh = open(filename, "w")
        logging.debug('URL: ' + filepath)
        logging.debug('FILENAME: ' + classname)        
        fh.write("#!/usr/bin/env python\n")

        #Write comment for creation date and author
        fh.write("\"\"\"")
        fh.write("\nCreated on " + now.strftime("%Y-%m-%d %H:%M"))
        fh.write("\n@author: Selenium Webdriver Code Generator\n")
        fh.write("\"\"\"\n")

        #Create page object header code by manipulating library code
        ph = open("lib/page_header.py", "r")
        fh.write("\n\n" + ph.read())
        ph.close()
        fh.write("\n\nclass " + classname + "(Base):\n") 
        
        #Write main comment for class
        fh.write("    \"\"\"\n")
        fh.write("    Variable definitions of  " + classname + " page object based on site HTML elements.\n") 
        fh.write("    \"\"\"")

        """
        Parse Title:
           (a) HTML Syntax: <title>CSCE 499 - Design Document</title>
           (b) BeautifulSoup Syntax: print soup.head.title
           (c) Variable Definition: _page_title = "CSCE 499 - Design Document"
           (d) Generated Selenium: The generated code should verify that the title string matches the ex-
               pected text as defined by the title variable.

        """
        logging.debug('Parse page title')
        fh.write("\n\n    # Page Title Variable")
        title = soup.head.title.string 
        gen = Generate()
        gen.generateVariable(fh, "_page_title", title)
        logging.debug('Title: ' + title)

        """
        All DIV with ID tag
           (a) HTML Syntax: <div id="banner-top">
           (b) BeautifulSoup Syntax: divs = soup.findAll('div','id':True)
           (c) Variable Definition: _div_banner_top_locator = (By.ID, "banner-top")
           (d) Generated Selenium: The generated code should verify that the DIV ID exists on the page.
        """
        
        logging.debug('Parse all DIVS with ids')
        fh.write("\n\n    # Variables defined by ID element")
        divs = soup.findAll('div',{'id':True})    
        for div in divs:
	    d = div['id']
            logging.debug(d)

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
        #CLIFF NOTE: Possibly delete or add debug condition for printing.
        logging.debug('Parse H1')
        h1s = soup.findAll('h1')    
        for h1 in h1s:
	    logging.debug(h1)

        """
        Image Files
           (a) HTML Syntax: <img src="/home-assets/images/banner-images/honors.jpg" alt="" border="0">
           (b) BeautifulSoup Syntax: imgs = soup.findAll('img')
           (c) Variable Definition: _img_honors_locator = (By.SRC, "/home-assets/images/banner-images/honors
           (d) Generated Selenium: The generat

        """
        #CLIFF NOTE: Possibly delete or add debug condition for printing.
        logging.debug('Parse Image')
        imgs = soup.findAll('img')    
        for img in imgs:
            logging.debug(img)
        """
        CLIFF NOTE: Re-investigate this one to see if it is really needed for testing
        """
        logging.debug('Parse iFrames')
        iframes = soup.findAll('iframe')    
        for iframe in iframes:
            logging.debug(iframe)

        """
        Radio Buttons
           (a) HTML Syntax: <input type="radio" name="group1" value="Cheese">
           (b) BeautifulSoup Syntax: radios = soup.findAll('input','type':'radio')
           (c) Variable Definition: _radio_cheese_locator = (By.Value, "Cheese")
           (d) Generated Selenium: The generated code should verify that the radio button exists, is selectable
               and simulates the "click" action in a basic sanity test.
        """
        #CLIFF NOTE: Possibly delete or add debug condition for printing.
        logging.debug('Parse Radio Buttons')
        radios = soup.findAll('input',{'type':'radio'})
        for radio in radios:
            logging.debug(radio)

        """
        Checkboxes
           (a) HTML Syntax: <input type="checkbox" name="sports" value="football">
           (b) BeautifulSoup Syntax: checkboxes = soup.findAll('input','type':'checkbox')
           (c) Variable Definition: _checkbox_sports_locator = (By.Value, "football")
           (d) Generated Selenium: The generated code should verify that the check box exists, is selectable
               and simulates the "click" action in a basic sanity test.
        """
        #CLIFF NOTE: Possibly delete or add debug condition for printing.
        logging.debug('Parse Checkbox Buttons')
        checkboxes = soup.findAll('input',{'type':'checkbox'})
        for checkbox in checkboxes:
            logging.debug(checkbox)

        """
        Text Fields
           (a) HTML Syntax: <textarea name="comments" cols="25" rows="5">Enter your comments here...
               </textarea>
           (b) BeautifulSoup Syntax: textboxes = soup.findAll('input','type':'text')
           (c) Variable Definition: _text_comments_locator = (By.Name, "comments")
           (d) Generated Selenium: The generated code should verify that the text area exists, is accessible
               by typing sample text and does not fail any SQL Injection negative test cases.
        """

        logging.debug('Parse Text Boxes')
        textboxes = soup.findAll('input',{'type':'text'})
        for textbox in textboxes:

            logging.debug(textbox)
            text_id = textbox.get('id')
            text_class = textbox.get('class')

            if text_id != "" and text_class != "" :
                out_str = ""
                for tc in text_class:
                    out_str += tc + "."
                
                if out_str[-1:] == '.':
                    out_str = out_str[:-1]

                #Print Class
                logging.debug(out_str)
                out_str2 = out_str.replace("-", "_")
                out_str2 = out_str2.replace(".", "_")
                varTextboxClass = "_textbox_class_" + out_str2 + "_locator"
                byCssSelectorSyntax = "(By.CSS_Selector, \""+ out_str + "\")"
                gen.generateVariable(fh, varTextboxClass, byCssSelectorSyntax)
                fh.write("\n")
                gen.generateFindElement(fh, varTextboxClass)

            if text_id  != "" and text_class == "":
                logging.debug(text_id)
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
                logging.debug(out_str)
        
                out_str2 = out_str.replace("-", "_")
                out_str2 = out_str2.replace(".", "_")
                varTextboxClass = "_textbox_class_" + out_str2 + "_locator"
                byCssSelectorSyntax = "(By.CSS_Selector, \""+ out_str + "\")"
                gen.generateVariable(fh, varTextboxClass, byCssSelectorSyntax)
                fh.write("\n")                
                gen.generateFindElement(fh, varTextboxClass)
   
        """
        Password Text Fields
           (a) HTML Syntax: <input type="password" size="25">
           (b) BeautifulSoup Syntax: passwords = soup.findAll('input','type':'password')
           (c) Variable Definition: _text_password_locator = (By.Type, "password")
           (d) Generated Selenium: The generated code should verify that the password text area exists, is
               accessible by typing hidden characters and does not fail any negative test case scenarios (e.g., SQL
               Injections and Security Tests).
        """
        #CLIFF NOTE: Possibly delete or add debug condition for printing.
        logging.debug('Parse Text Box')
        passwords = soup.findAll('input',{'type':'password'})
        for password in passwords:
            logging.debug(password)
    
        """
        Buttons
           (a) HTML Syntax: <input type="submit" value="Submit">
           (b) BeautifulSoup Syntax: button = soup.findAll('input','type':'submit')
           (c) Variable Definition: _button_submit_locator = (By.Type, "submit")
           (d) Generated Selenium: The generated code should verify that the button exists, is able to be
               clicked and functions correctly when selected.
        """
        #CLIFF NOTE: Possibly delete or add debug condition for printing.
        logging.debug('Parse Buttons')
        buttons = soup.findAll('input',{'type':'submit'})
        for button in buttons:
            logging.debug(button)

        #Extract base name for url
        o = urlparse.urlparse(url)
        bname = basename(o.path)
        logging.debug('Base Name: ' + bname)

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
            logging.debug(d)
            varName = "_id_" + d.replace("-", "_") + "_locator"
            methodName = "is" + varName + "_available"
            testMethods.append(methodName)
            gen.generateFindElement(fh, varName)

        fh.close()

        if classname != "":
            gen.generateTestElement(classname, filetext, testMethods)    


def getLinks(url):

    """
    CLIFF NOTE: ADD FUNCTION COMMENT HERE
    """
    logging.debug('Get Links')
    page = Fetcher(url)
    page.fetch()
    for u, url in enumerate(page):
        logging.info("%d. %s" % (u, url))


def parse_cmd_line():
       
    """
    Parse command-line arguements

    FUTURE WORK: Replace OptionParses (old) with argparse (new)
    """

    parser = optparse.OptionParser()

    parser.add_option("-l", "--links",
                      action="store_true", default=True, dest="links",
                      help="Only get links for specific URL")    

    parser.add_option("-d", "--depth",
                      action="store", type="int", default=25, dest="depth_max",
                      help="Maximum depth to crawl")

    parser.add_option("-r", "--restrict",
                      action="store", type="string", dest="restrict",
                      help="Limit crawl to specific prefix")
    
    parser.add_option("-o", "--output", action="store", type="string", default="SeleniumAuto",
                      dest="output", help="Output Directory to Generate To")


    options, arguements = parser.parse_args()

    if len(arguements) < 1:
        parser.print_help(sys.stderr)
        raise SystemExit, 1

    return options, arguements


def main():    

    """
    CLIFF NOTE: ADD FUNCTION COMMENT HERE
    """
    LOG_FILENAME = 'generator.log'

    logging.basicConfig(filename=LOG_FILENAME,filemode='w',level=logging.DEBUG)
    logging.info('Starting auto-generator')
    logging.debug('Initializing variables')

    options, arguements = parse_cmd_line()
    global dest_dir # Output folder used throughout...
    dest_dir = options.output
    url = arguements[0]

    logging.debug('Initializing new framework')
    gen = Generate()
    gen.generateFramework()

    depth_max = options.depth_max
    restrict_prefix=options.restrict
    sTime = time.time()

    #Copy all prerequisite files
    logging.debug('Coping all prerequisite files to new framework')
    src1 = "conftest.py"
    src2 = "credentials.yaml"
    src3 = "mozwebqa.cfg"
    src4 = "README.md"
    src5 = "requirements.txt"
    src6 = "page.py"
    src7 = "__init__.py"
    src8 = "base.py"

    logging.info('Destination Directory: ' + dest_dir)

    gen.copyAnything("lib/" + src1, dest_dir + "/" + src1)
    gen.copyAnything("lib/" + src2, dest_dir + "/" + src2)
    gen.copyAnything("lib/" + src3, dest_dir + "/" + src3)
    gen.copyAnything("lib/" + src4, dest_dir + "/" + src4)
    gen.copyAnything("lib/" + src5, dest_dir + "/" + src5)

    logging.debug('Configuring MOZWEBQA.CFG')
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

    if options.links:
        getLinks(url)
        raise SystemExit, 0

    print >> sys.stderr,  "Crawling %s (Max Depth: %d)" % (url, depth_max)
    logging.debug('Begin crawling URL based on prerequisite filters')
    crawler = Spider(url, depth_max, restrict_prefix)
    crawler.crawl()

    eTime = time.time()
    tTime = eTime - sTime

    print >> sys.stderr, "Found:    %d" % crawler.count_links
    print >> sys.stderr, "Followed: %d" % crawler.count_followed

if __name__ == "__main__":
    main()
