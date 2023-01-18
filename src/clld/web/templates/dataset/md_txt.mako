<%! from clld.web.util import doi %>${request.dataset.formatted_editors()|n} (eds.) ${request.dataset.published.year if request.dataset.published else request.dataset.updated.year}.
% if req.registry.settings.get('clld.zenodo_version_tag') and req.registry.settings.get('clld.zenodo_version_doi'):
${request.dataset.name} (${req.registry.settings['clld.zenodo_version_tag']}) [Data set]. Zenodo.
${doi.url(req.registry.settings['clld.zenodo_version_doi'])}
% elif req.registry.settings.get('clld.zenodo_concept_doi'):
${request.dataset.name} [Data set]. Zenodo.
${doi.url(req.registry.settings['clld.zenodo_concept_doi'])}
% else:
${request.dataset.description or request.dataset.name}.
${request.dataset.publisher_place}: ${request.dataset.publisher_name}.
% endif
(Available online at https://${request.dataset.domain}, Accessed on ${h.datetime.date.today()}.)
