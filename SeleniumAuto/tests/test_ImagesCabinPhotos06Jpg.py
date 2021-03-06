#!/usr/bin/env python
import pytest
from unittestzero import Assert
from pages.imagescabinphotos06jpg import ImagesCabinPhotos06Jpg

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

class ImagesCabinPhotos06Jpg:

    @pytest.mark.nondestructive
    def test_is_id_container_locator_available(self, mozwebqa):

        page = ImagesCabinPhotos06Jpg(mozwebqa)
        Assert.true(page.is_id_container_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_mainContent_locator_available(self, mozwebqa):

        page = ImagesCabinPhotos06Jpg(mozwebqa)
        Assert.true(page.is_id_mainContent_locator_available)
