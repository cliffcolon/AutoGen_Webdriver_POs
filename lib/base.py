#!/usr/bin/env python

import re

from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from pages.page import Page


class Base(Page):
    """
    The Base object provides common methods for all Page Objects
    """

    @property
    def page_title(self):
        """
        Method to get the current pages title.
        """
        WebDriverWait(self.selenium, 10).until(lambda s: self.selenium.title)
        return self.selenium.title

    def credentials_of_user(self, user):
        """
        Method to return the user from the yaml config file
        """
        return self.parse_yaml_file(self.credentials)[user]


