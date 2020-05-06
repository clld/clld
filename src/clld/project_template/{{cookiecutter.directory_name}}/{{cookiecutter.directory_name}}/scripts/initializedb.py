from clld.cliutil import Data
from clld.db.models import common
{% if cookiecutter.cldf_module %}
from clld_glottologfamily_plugin.util import load_families
{% endif %}

import {{cookiecutter.directory_name}}
from {{cookiecutter.directory_name}} import models


def iteritems(cldf, t, *cols):
    cmap = {cldf[t, col].name: col for col in cols}
    for item in cldf[t]:
        for k, v in cmap.items():
            item[v] = item[k]
        yield item


def main(args):
{% if cookiecutter.cldf_module %}
    assert args.glottolog, 'The --glottolog option is required!'
{% endif %}
    data = Data()
    data.add(
        common.Dataset,
        {{cookiecutter.directory_name}}.__name__,
        id={{cookiecutter.directory_name}}.__name__,
        domain='{{cookiecutter.domain}}',
{% if cookiecutter.mpg %}
        publisher_name="Max Planck Institute for the Science of Human History",
        publisher_place="Jena",
        publisher_url="http://www.shh.mpg.de",
        license="http://creativecommons.org/licenses/by/4.0/",
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'},
{% endif %}
    )

{% if cookiecutter.cldf_module %}
    contrib = data.add(
        common.Contribution,
        None,
        id='cldf',
        name=args.cldf.properties.get('dc:title'),
        description=args.cldf.properties.get('dc:bibliographicCitation'),
    )

    for lang in iteritems(args.cldf, 'LanguageTable', 'id', 'glottocode', 'name', 'latitude', 'longitude'):
        data.add(
            models.Variety,
            lang['id'],
            id=lang['id'],
            name=lang['name'],
            latitude=lang['latitude'],
            longitude=lang['longitude'],
            glottocode=lang['glottocode'],
        )

{% if cookiecutter.cldf_module.lower() == 'wordlist' %}
    for param in iteritems(args.cldf, 'ParameterTable', 'id', 'concepticonReference', 'name'):
        data.add(
            models.Concept,
            param['id'],
            id=param['id'],
            name='{} [{}]'.format(param['name'], param['id']),
        )
    for form in iteritems(args.cldf, 'FormTable', 'id', 'form', 'languageReference', 'parameterReference'):
        vsid = (form['languageReference'], form['parameterReference'])
        vs = data['ValueSet'].get(vsid)
        if not vs:
            vs = data.add(
                common.ValueSet,
                vsid,
                id='-'.join(vsid),
                language=data['Variety'][form['languageReference']],
                parameter=data['Concept'][form['parameterReference']],
                contribution=contrib,
            )
        data.add(
            common.Value,
            form['id'],
            id=form['id'],
            name=form['form'],
            valueset=vs,
        )
{% elif cookiecutter.cldf_module.lower() == 'structuredataset' %}
    for param in iteritems(args.cldf, 'ParameterTable', 'id', 'name'):
        data.add(
            models.Feature,
            param['id'],
            id=param['id'],
            name='{} [{}]'.format(param['name'], param['id']),
    )
    for val in iteritems(args.cldf, 'ValueTable', 'id', 'value', 'languageReference', 'parameterReference'):
        # FIXME: also get codeReference!
        vsid = (val['languageReference'], val['parameterReference'])
        vs = data['ValueSet'].get(vsid)
        if not vs:
            vs = data.add(
                common.ValueSet,
                vsid,
                id='-'.join(vsid),
                language=data['Variety'][val['languageReference']],
                parameter=data['Feature'][val['parameterReference']],
                contribution=contrib,
            )
        data.add(
            common.Value,
            val['id'],
            id=val['id'],
            name=val['form'],
            valueset=vs,
        )
{% endif %}
load_families(
    Data(),
    [(l.glottocode, l) for l in data['Variety'].values()],
        glottolog_repos=args.glottolog,
        isolates_icon='tcccccc',
        strict=False,
    )
{% endif %}


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
