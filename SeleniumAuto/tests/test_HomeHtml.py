#!/usr/bin/env python
import pytest
from unittestzero import Assert
from pages.homehtml import HomeHtml

class HeaderMenu:

    def __init__(self, name, items):
        self.name = name
        self.items = items

    @property
    def name(self):
        return self.name

    @property
    def items(self):
        return self.items

class HomeHtml:

    @pytest.mark.nondestructive
    def test_is_id_container_locator_available(self, mozwebqa):

        page = HomeHtml(mozwebqa)
        Assert.true(page.is_id_container_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_mainContent_locator_available(self, mozwebqa):

        page = HomeHtml(mozwebqa)
        Assert.true(page.is_id_mainContent_locator_available)
