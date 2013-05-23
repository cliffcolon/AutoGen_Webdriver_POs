#!/usr/bin/env python
"""
Created on 2013-05-01 21:44
@author: Selenium Webdriver Code Generator
"""
import pytest
from unittestzero import Assert
from pages.auto.coursescsce499acfestschedulehtml import CoursesCsce499AcfestScheduleHtml
class TestCoursesCsce499AcfestScheduleHtml:

    @pytest.mark.nondestructive
    def test_is_id_banner_top_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499AcfestScheduleHtmlpage object: coursescsce499acfestschedulehtml.py
        """
        page = CoursesCsce499AcfestScheduleHtml(mozwebqa)
        Assert.true(page.is_id_banner_top_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_nav_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499AcfestScheduleHtmlpage object: coursescsce499acfestschedulehtml.py
        """
        page = CoursesCsce499AcfestScheduleHtml(mozwebqa)
        Assert.true(page.is_id_nav_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_main_content_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499AcfestScheduleHtmlpage object: coursescsce499acfestschedulehtml.py
        """
        page = CoursesCsce499AcfestScheduleHtml(mozwebqa)
        Assert.true(page.is_id_main_content_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_bd_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499AcfestScheduleHtmlpage object: coursescsce499acfestschedulehtml.py
        """
        page = CoursesCsce499AcfestScheduleHtml(mozwebqa)
        Assert.true(page.is_id_bd_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_ft_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499AcfestScheduleHtmlpage object: coursescsce499acfestschedulehtml.py
        """
        page = CoursesCsce499AcfestScheduleHtml(mozwebqa)
        Assert.true(page.is_id_ft_locator_available)
