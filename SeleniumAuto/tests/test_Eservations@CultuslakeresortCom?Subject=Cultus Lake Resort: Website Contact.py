#!/usr/bin/env python
import pytest
from unittestzero import Assert
from pages.eservations@cultuslakeresortcom?subject=cultus lake resort: website contact import Eservations@CultuslakeresortCom?Subject=Cultus Lake Resort: Website Contact

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

class Eservations@CultuslakeresortCom?Subject=Cultus Lake Resort: Website Contact:

    @pytest.mark.nondestructive
    def test_is_id_container_locator_available(self, mozwebqa):

        page = Eservations@CultuslakeresortCom?Subject=Cultus Lake Resort: Website Contact(mozwebqa)
        Assert.true(page.is_id_container_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_mainContent_locator_available(self, mozwebqa):

        page = Eservations@CultuslakeresortCom?Subject=Cultus Lake Resort: Website Contact(mozwebqa)
        Assert.true(page.is_id_mainContent_locator_available)
