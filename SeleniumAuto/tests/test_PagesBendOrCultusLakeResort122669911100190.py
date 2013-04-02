#!/usr/bin/env python
import pytest
from unittestzero import Assert
from pages.pagesbendorcultuslakeresort122669911100190 import PagesBendOrCultusLakeResort122669911100190

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

class PagesBendOrCultusLakeResort122669911100190:

    @pytest.mark.nondestructive
    def test_is_id_container_locator_available(self, mozwebqa):

        page = PagesBendOrCultusLakeResort122669911100190(mozwebqa)
        Assert.true(page.is_id_container_locator_available)
