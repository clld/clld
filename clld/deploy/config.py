from path import path


SERVERS = ['cldbstest', 'clld1', 'clld3', 'clld2', 'cldbs']


def repos(name):
    return 'git://github.com/clld/%s.git' % name


class App(object):
    def __init__(self, name, port, **kw):
        self.name = name
        self.port = port
        self.host = kw.get('host', '%s.clld.org' % name)

        kw.setdefault('workers', 5)
        kw.setdefault('deploy_duration', 1)
        kw.setdefault('production', SERVERS[0])
        kw.setdefault('test', SERVERS[1])
        for k, v in kw.items():
            setattr(self, k, v)
        assert self.production != self.test

    @property
    def src(self):
        return self.venv.joinpath('src', self.name)

    @property
    def venv(self):
        return path('/usr/venvs').joinpath(self.name)

    @property
    def home(self):
        return path('/home').joinpath(self.name)

    @property
    def pages(self):
        if getattr(self, '_pages', False):
            return self.home.joinpath('%s-pages' % self.name)

    @property
    def newrelic_log(self):
        return self.home.joinpath('newrelic.log')

    @property
    def www(self):
        return self.home.joinpath('www')

    @property
    def config(self):
        return self.home.joinpath('config.ini')

    @property
    def newrelic_config(self):
        return self.home.joinpath('newrelic.ini')

    @property
    def logs(self):
        return path('/var/log').joinpath(self.name)

    @property
    def error_log(self):
        return self.logs.joinpath('error.log')

    def bin(self, command):
        return self.venv.joinpath('bin', command)

    @property
    def supervisor(self):
        return path('/etc/supervisor/conf.d').joinpath('%s.conf' % self.name)

    @property
    def nginx_location(self):
        return path('/etc/nginx/locations.d').joinpath('%s.conf' % self.name)

    @property
    def nginx_htpasswd(self):
        return path('/etc/nginx/locations.d').joinpath('%s.htpasswd' % self.name)

    @property
    def nginx_site(self):
        return path('/etc/nginx/sites-enabled').joinpath(self.name)

    @property
    def sqlalchemy_url(self):
        return 'postgresql://{0}@/{0}'.format(self.name)


APPS = dict((app.name, app) for app in [
    App('ids', 8893, test=SERVERS[0], production=SERVERS[2]),
    App('valpal', 8892, test=SERVERS[2], production=SERVERS[3]),
    App('waab', 8891, domain="afbo.info", test=SERVERS[0], production=SERVERS[2]),
    App('phoible', 8890, domain='phoible.org', test=SERVERS[1], production=SERVERS[2]),
    App('glottologcurator', 8889, test=SERVERS[1], workers=1, dependencies=['glottolog3']),
    App('wold2', 8888, domain='wold.livingsources.org', test=SERVERS[0], production=SERVERS[1]),
    App('wals3', 8887, domain='wals.info', workers=7, test=SERVERS[2], production=SERVERS[0], with_blog=True),
    App('apics', 8886, domain='apics-online.info', test=SERVERS[0], production=SERVERS[1]),
    App('jcld', 8884, test=SERVERS[0], production=SERVERS[4], _pages=True, domain='jcld.clld.org'),
    App('wow', 8883, test=SERVERS[1]),
    App('ewave', 8882, domain='ewave-atlas.org', test=SERVERS[1], production=SERVERS[2]),
    App('glottolog3', 8881, domain='glottolog.org', deploy_duration=2, workers=5, test=SERVERS[1], production=SERVERS[0]),
    App('solr', 8080),
])

ERROR_EMAIL = 'robert_forkel@eva.mpg.de'
