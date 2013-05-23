#!/usr/bin/env python

import py

def pytest_runtest_setup(item):
    pytest_mozwebqa = py.test.config.pluginmanager.getplugin("mozwebqa")
    pytest_mozwebqa.TestSetup.api_base_url = item.config.option.api_base_url


def pytest_addoption(parser):
    parser.addoption("--apibaseurl",
                     action="store",
                     dest='api_base_url',
                     metavar='str',
                     default="https://www.cs.plu.edu/courses/csce499/current/",
                     help="specify the api url")


def pytest_funcarg__mozwebqa(request):
    pytest_mozwebqa = py.test.config.pluginmanager.getplugin("mozwebqa")
    return pytest_mozwebqa.TestSetup(request)
