#!/usr/bin/env python

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from pages.page import Page
from pages.base import Base



class ImagesCabinPhotos06Jpg(Base):


    # Page Title Variable
    _page_title = "Cabins | Cultus Lake Resort | Oregon"

    # Variables defined by ID element
    _id_container_locator = (By.ID, "container")
    _id_mainContent_locator = (By.ID, "mainContent")

    @property
    def is_id_container_locator_available(self):
        return self.is_element_visible(*self._id_container_locator)

    @property
    def is_id_mainContent_locator_available(self):
        return self.is_element_visible(*self._id_mainContent_locator)
