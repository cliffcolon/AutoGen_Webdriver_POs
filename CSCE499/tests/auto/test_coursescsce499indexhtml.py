#!/usr/bin/env python
"""
Created on 2013-05-01 21:44
@author: Selenium Webdriver Code Generator
"""
import pytest
from unittestzero import Assert
from pages.auto.coursescsce499indexhtml import CoursesCsce499IndexHtml
class TestCoursesCsce499IndexHtml:

    @pytest.mark.nondestructive
    def test_is_id_banner_top_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499IndexHtmlpage object: coursescsce499indexhtml.py
        """
        page = CoursesCsce499IndexHtml(mozwebqa)
        Assert.true(page.is_id_banner_top_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_nav_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499IndexHtmlpage object: coursescsce499indexhtml.py
        """
        page = CoursesCsce499IndexHtml(mozwebqa)
        Assert.true(page.is_id_nav_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_main_content_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499IndexHtmlpage object: coursescsce499indexhtml.py
        """
        page = CoursesCsce499IndexHtml(mozwebqa)
        Assert.true(page.is_id_main_content_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_bd_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499IndexHtmlpage object: coursescsce499indexhtml.py
        """
        page = CoursesCsce499IndexHtml(mozwebqa)
        Assert.true(page.is_id_bd_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_ft_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499IndexHtmlpage object: coursescsce499indexhtml.py
        """
        page = CoursesCsce499IndexHtml(mozwebqa)
        Assert.true(page.is_id_ft_locator_available)
