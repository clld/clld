from clld.tests.util import TestWithApp


class Tests(TestWithApp):
    def test_robots(self):
        res = self.app.get('/robots.txt', status=200)

    def test_sitemap(self):
        res = self.app.get('/sitemap.xml', status=200)
