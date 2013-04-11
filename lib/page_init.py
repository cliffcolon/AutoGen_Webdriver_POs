    def __init__(self, testsetup, open_url=True):
        """Creates a new instance of the class and gets the page ready for testing."""
        Base.__init__(self, testsetup)
        if open_url:
            self.selenium.get(self.base_url + "/{{WILDCARD4}}")
