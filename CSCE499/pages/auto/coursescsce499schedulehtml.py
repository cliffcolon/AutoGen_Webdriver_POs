#!/usr/bin/env python
"""
Created on 2013-05-01 21:44
@author: Selenium Webdriver Code Generator
"""


import re

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from pages.page import Page
from pages.auto.base import Base


class CoursesCsce499ScheduleHtml(Base):
    """
    Variable definitions of  CoursesCsce499ScheduleHtml page object based on site HTML elements.
    """

    # Page Title Variable
    _page_title = "CSCE 499 - Home"

    # Variables defined by ID element
    _id_banner_top_locator = (By.ID, "banner-top")
    _id_nav_locator = (By.ID, "nav")
    _id_main_content_locator = (By.ID, "main-content")
    _id_bd_locator = (By.ID, "bd")
    _id_ft_locator = (By.ID, "ft")

    def __init__(self, testsetup, open_url=True):
        """Creates a new instance of the class and gets the page ready for testing."""
        Base.__init__(self, testsetup)
        if open_url:
            self.selenium.get(self.base_url + "/schedule.html")


    @property
    def is_id_banner_top_locator_available(self):
        return self.is_element_visible(*self._id_banner_top_locator)

    @property
    def is_id_nav_locator_available(self):
        return self.is_element_visible(*self._id_nav_locator)

    @property
    def is_id_main_content_locator_available(self):
        return self.is_element_visible(*self._id_main_content_locator)

    @property
    def is_id_bd_locator_available(self):
        return self.is_element_visible(*self._id_bd_locator)

    @property
    def is_id_ft_locator_available(self):
        return self.is_element_visible(*self._id_ft_locator)
