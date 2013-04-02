#!/usr/bin/env python
import pytest
from unittestzero import Assert
from pages.weekendguidetraveltascenicdrivesbendlapineoregonsidwcmdev052631html import WeekendGuideTravelTaScenicDrivesBendLaPineOregonSidwcmdev052631Html

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

class WeekendGuideTravelTaScenicDrivesBendLaPineOregonSidwcmdev052631Html:

    @pytest.mark.nondestructive
    def test_is_id_container_locator_available(self, mozwebqa):

        page = WeekendGuideTravelTaScenicDrivesBendLaPineOregonSidwcmdev052631Html(mozwebqa)
        Assert.true(page.is_id_container_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_mainContent_locator_available(self, mozwebqa):

        page = WeekendGuideTravelTaScenicDrivesBendLaPineOregonSidwcmdev052631Html(mozwebqa)
        Assert.true(page.is_id_mainContent_locator_available)
