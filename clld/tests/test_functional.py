from clld.tests.util import TestWithApp


class Tests(TestWithApp):
    def test_robots(self):
        self.app.get('/robots.txt', status=200)

    def test_sitemap(self):
        self.app.get('/sitemap.xml', status=200)

    def test_language(self):
        #self.app.get('/language/l1', headers={'accept': 'text/html'}, status=200)
        self.app.get('/languages', headers={'accept': 'text/html'}, status=200)
