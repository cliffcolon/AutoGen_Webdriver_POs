#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import py

def pytest_runtest_setup(item):
    pytest_mozwebqa = py.test.config.pluginmanager.getplugin("mozwebqa")
    pytest_mozwebqa.TestSetup.api_base_url = item.config.option.api_base_url
    pytest_mozwebqa.TestSetup.db_name_str = item.config.option.db_name_str
    pytest_mozwebqa.TestSetup.db_user_str = item.config.option.db_user_str
    pytest_mozwebqa.TestSetup.db_pass_str = item.config.option.db_pass_str
    pytest_mozwebqa.TestSetup.theme_str = item.config.option.theme_str
    pytest_mozwebqa.TestSetup.admin_str = item.config.option.admin_str
    pytest_mozwebqa.TestSetup.testing_profile = item.config.option.testing_profile
    pytest_mozwebqa.TestSetup.site_region_str = item.config.option.site_region_str
    pytest_mozwebqa.TestSetup.site_brand_str = item.config.option.site_brand_str

def pytest_addoption(parser):
    parser.addoption("--apibaseurl",
                     action="store",
                     dest='api_base_url',
                     metavar='str',
                     default="https://addons-dev.allizom.org",
                     help="specify the api url")
    parser.addoption("--dbname",
                     action="store",
                     dest='db_name_str',
                     metavar='str',
                     default="nextgen",
                     help="The name of the database")
    parser.addoption("--dbuser",
                     action="store",
                     dest='db_user_str',
                     metavar='str',
                     default="root",
                     help="The username of the database")
    parser.addoption("--dbpass",
                     action="store",
                     dest='db_pass_str',
                     metavar='str',
                     default="password",
                     help="The password of the database")
    parser.addoption("--theme",
                     action="store",
                     dest='theme_str',
                     metavar='str',
                     default="SPTI Base Theme",
                     help="Drupal site default theme")
    parser.addoption("--admintheme",
                     action="store",
                     dest='admin_str',
                     metavar='str',
                     default="SPT admin",
                     help="Drupal administration menu theme")
    parser.addoption("--testing",
                     action="store_true",
                     dest='testing_profile',
                     default=False,
                     help="Drupal installation profile")
    parser.addoption("--region",
                     action="store",
                     dest='site_region_str',
                     metavar='str',
                     default="United States",
                     help="configure site region")
    parser.addoption("--brand",
                     action="store",
                     dest='site_brand_str',
                     metavar='str',
                     default="Next Gen [Development]",
                     help="configure site brand")


def pytest_funcarg__mozwebqa(request):
    pytest_mozwebqa = py.test.config.pluginmanager.getplugin("mozwebqa")
    return pytest_mozwebqa.TestSetup(request)
