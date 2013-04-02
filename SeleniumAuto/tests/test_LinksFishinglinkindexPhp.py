#!/usr/bin/env python
import pytest
from unittestzero import Assert
from pages.linksfishinglinkindexphp import LinksFishinglinkindexPhp

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

class LinksFishinglinkindexPhp:

    @pytest.mark.nondestructive
    def test_is_id_container_locator_available(self, mozwebqa):

        page = LinksFishinglinkindexPhp(mozwebqa)
        Assert.true(page.is_id_container_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_mainContent_locator_available(self, mozwebqa):

        page = LinksFishinglinkindexPhp(mozwebqa)
        Assert.true(page.is_id_mainContent_locator_available)
