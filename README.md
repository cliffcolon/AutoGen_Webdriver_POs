Auto-Generated Selenium Webdriver Test Automation Code using Page Objects for Content Management Systems
======================

Developing test automation code for a web project often requires more time defining the specific test objects than the bandwidth allocated for the test engineer. since all of the tedious automation framework coding is automatically created, auto-generating the test automation code and test framework can provide a test team with a huge advantage when attempting to provide a well defined test process to a software project. This allows the test automation engineer to focus more on the specific test cases and less on the object definitions/API calls used. In order to achieve this goal, this project will use a unique concept in many QA teams: create automation code to create automation code. This automation framework would be very valuable to companies looking to quickly add a layer of test automation to their website project.

Use Case Scenario
===========================

The main goal is to develop automation code that auto-generates Selenium Webdriver test code, written in Python, that makes use of page objects and can be used for providing test automation for Content Management Systems (CMS). The end user (Ex: test engineer) should be able to perform the following steps:

1. Download the automation framework (Ex: Git Clone)
2. Install/Configure all of the required Linux tools necessary for executing the automation framework.
3. Enter the base URL of the CMS to generate the automation code.
4. Run the test automation tool on the CMS URL through Linux command line.
5. The project will crawl through all (or all main) site pages and will extract all elements/properties that can be used for site testing.
6. After the site crawl process is complete, the automation tool will generate all of the test automation page objects in Python based on the elements discovered during the site crawl.
7. Page objects will use a standard naming convention for classes and function definitions.
8. The automation project will also generate a set of generic sanity test cases that will execute all of the generated page object definitions.
9. The test framework will generate a test report (HTML), using a tool such as PyTest, and will display a summary of the test execution in the Linux command line window.
10. All auto-generated code will also generate embedded Python Sphinx commenting, which will allow for the automated creation of source code documentation (HTML, LaTeX, plain text, etc).
11. The test automation code should be able to run after generation without any errors.