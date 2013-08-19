from clld.tests.util import TestWithApp


class Tests(TestWithApp):
    def test_robots(self):
        self.app.get('/robots.txt', status=200)

    def test_sitemapindex(self):
        self.app.get('/sitemap.xml', status=200)

    def test_sitemap(self):
        self.app.get('/sitemap.language.0.xml', status=200)

    def test_language(self):
        self.app.get('/languages', status=200)
        self.app.get('/languages?sEcho=1&iDisplayLength=5', xhr=True, status=200)
