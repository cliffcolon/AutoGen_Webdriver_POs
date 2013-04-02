#!/usr/bin/env python

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from pages.page import Page
from pages.base import Base



class DeckHtml(Base):


    # Page Title Variable
    _page_title = "Cultus Lake Resort | Deschutes National Forest | Oregon"

    # Variables defined by ID element
    _id_container_locator = (By.ID, "container")

    @property
    def is_id_container_locator_available(self):
        return self.is_element_visible(*self._id_container_locator)
