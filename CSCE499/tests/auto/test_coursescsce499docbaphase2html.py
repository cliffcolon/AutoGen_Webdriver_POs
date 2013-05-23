#!/usr/bin/env python
"""
Created on 2013-05-01 21:44
@author: Selenium Webdriver Code Generator
"""
import pytest
from unittestzero import Assert
from pages.auto.coursescsce499docbaphase2html import CoursesCsce499DocBaPhase2Html
class TestCoursesCsce499DocBaPhase2Html:

    @pytest.mark.nondestructive
    def test_is_id_banner_top_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499DocBaPhase2Htmlpage object: coursescsce499docbaphase2html.py
        """
        page = CoursesCsce499DocBaPhase2Html(mozwebqa)
        Assert.true(page.is_id_banner_top_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_nav_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499DocBaPhase2Htmlpage object: coursescsce499docbaphase2html.py
        """
        page = CoursesCsce499DocBaPhase2Html(mozwebqa)
        Assert.true(page.is_id_nav_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_main_content_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499DocBaPhase2Htmlpage object: coursescsce499docbaphase2html.py
        """
        page = CoursesCsce499DocBaPhase2Html(mozwebqa)
        Assert.true(page.is_id_main_content_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_bd_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499DocBaPhase2Htmlpage object: coursescsce499docbaphase2html.py
        """
        page = CoursesCsce499DocBaPhase2Html(mozwebqa)
        Assert.true(page.is_id_bd_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_ft_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499DocBaPhase2Htmlpage object: coursescsce499docbaphase2html.py
        """
        page = CoursesCsce499DocBaPhase2Html(mozwebqa)
        Assert.true(page.is_id_ft_locator_available)
