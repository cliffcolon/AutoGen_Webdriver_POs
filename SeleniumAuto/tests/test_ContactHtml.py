#!/usr/bin/env python
import pytest
from unittestzero import Assert
from pages.contacthtml import ContactHtml

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

class ContactHtml:

    @pytest.mark.nondestructive
    def test_is_id_container_locator_available(self, mozwebqa):

        page = ContactHtml(mozwebqa)
        Assert.true(page.is_id_container_locator_available)
