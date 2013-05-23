#!/usr/bin/env python
"""
Created on 2013-05-01 21:44
@author: Selenium Webdriver Code Generator
"""
import pytest
from unittestzero import Assert
from pages.auto.coursescsce499designpresentationschedulehtml import CoursesCsce499DesignPresentationScheduleHtml
class TestCoursesCsce499DesignPresentationScheduleHtml:

    @pytest.mark.nondestructive
    def test_is_id_banner_top_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499DesignPresentationScheduleHtmlpage object: coursescsce499designpresentationschedulehtml.py
        """
        page = CoursesCsce499DesignPresentationScheduleHtml(mozwebqa)
        Assert.true(page.is_id_banner_top_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_nav_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499DesignPresentationScheduleHtmlpage object: coursescsce499designpresentationschedulehtml.py
        """
        page = CoursesCsce499DesignPresentationScheduleHtml(mozwebqa)
        Assert.true(page.is_id_nav_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_main_content_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499DesignPresentationScheduleHtmlpage object: coursescsce499designpresentationschedulehtml.py
        """
        page = CoursesCsce499DesignPresentationScheduleHtml(mozwebqa)
        Assert.true(page.is_id_main_content_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_bd_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499DesignPresentationScheduleHtmlpage object: coursescsce499designpresentationschedulehtml.py
        """
        page = CoursesCsce499DesignPresentationScheduleHtml(mozwebqa)
        Assert.true(page.is_id_bd_locator_available)

    @pytest.mark.nondestructive
    def test_is_id_ft_locator_available(self, mozwebqa):

        """
        Test pages elements defined in CoursesCsce499DesignPresentationScheduleHtmlpage object: coursescsce499designpresentationschedulehtml.py
        """
        page = CoursesCsce499DesignPresentationScheduleHtml(mozwebqa)
        Assert.true(page.is_id_ft_locator_available)
