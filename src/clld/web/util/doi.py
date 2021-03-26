from clld.web.util.htmllib import HTML

__all__ = ['BASE_URL', 'get_doi', 'url', 'logo', 'link', 'badge']

BASE_URL = 'https://doi.org'


def get_doi(obj):
    if isinstance(obj, str):
        return obj
    return getattr(obj, 'doi', getattr(obj, 'jsondata', {}).get('doi'))


def url(obj):
    doi = get_doi(obj)
    if doi:
        return '{0}/{1}'.format(BASE_URL, doi)


def logo(req, width='20'):
    return HTML.img(
        src=req.static_url('clld:web/static/images/doi_logo.png'),
        width=width,
        style="margin-top: -2px")


def link(req, obj, label=None, with_logo=True):
    doi = get_doi(obj)
    akw = dict(title='DOI: {}'.format(doi), href=url(doi))
    return HTML.a(logo(req) if with_logo else '', label or doi, **akw)


def badge(obj):
    doi = get_doi(obj)
    if doi.startswith('10.5281/zenodo.'):
        return HTML.a(
            HTML.img(
                src="https://zenodo.org/badge/DOI/{}.svg".format(doi), alt='DOI: {}'.format(doi)),
            href=url(doi))
