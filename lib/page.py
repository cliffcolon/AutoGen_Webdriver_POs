#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Change for a pull request test

'''
Created on Jun 21, 2010

'''
from unittestzero import Assert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException


class Page(object):
    """
    Base class with general methods for all Pages.
    """

    def __init__(self, testsetup):
        """
        Constructor
        """
        self.testsetup = testsetup
        self.base_url = testsetup.base_url
        self.db_name_str = testsetup.db_name_str
        self.db_user_str = testsetup.db_user_str
        self.db_pass_str = testsetup.db_pass_str
        self.theme_str = testsetup.theme_str
        self.admin_str = testsetup.admin_str
        self.testing_profile = testsetup.testing_profile
        self.api_base_url = testsetup.api_base_url
        self.selenium = testsetup.selenium
        self.timeout = testsetup.timeout
        self.site_region_str = testsetup.site_region_str
        self.site_brand_str = testsetup.site_brand_str


    def get_url(self, url):
        """
        Method to send the current url to selenium.
        """
        self.selenium.get(url)

    @property
    def is_the_current_page(self):
        """
        Method to verify that the current page is correct.
        """
        if self._page_title:
            WebDriverWait(self.selenium, 10).until(lambda s: self.selenium.title)

        Assert.equal(self.selenium.title, self._page_title,
            "Expected page title: %s. Actual page title: %s" % (self._page_title, self.selenium.title))
        return True

    def get_url_current_page(self):
        """
        Method to get the current url.
        """
        WebDriverWait(self.selenium, 10).until(lambda s: self.selenium.title)
        return self.selenium.current_url

    def is_element_present(self, *locator):
        """
        General method to verify a web element is present.
        """
        self.selenium.implicitly_wait(0)
        try:
            self.selenium.find_element(*locator)
            return True
        except NoSuchElementException:
            return False
        finally:
            # set back to where you once belonged
            self.selenium.implicitly_wait(self.testsetup.default_implicit_wait)

    def is_element_visible(self, *locator):
        """
        General method to verify web element is visible
        """
        try:
            return self.selenium.find_element(*locator).is_displayed()
        except NoSuchElementException, ElementNotVisibleException:
            return False

    def return_to_previous_page(self):
        """
        Method to go back a page.
        """
        self.selenium.back()
