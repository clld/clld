<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>

<h3>Downloads</h3>

% if req.registry.settings.get('clld.zenodo_concept_doi'):
${util.dataset_download()}
% else:
<div class="span5 well well-small">
    <dl>
        % for model, dls in h.get_downloads(request):
        <dt>${_(model)}</dt>
        % for dl in dls:
        <dd>
            <a href="${dl.url(request)}">${dl.label(req)}</a>
        </dd>
        % endfor
        % endfor
    </dl>
</div>
<div class="span6">
    <p>
        Downloads are provided as
        ${h.external_link("http://en.wikipedia.org/wiki/Zip_%28file_format%29", label="zip archives")}
        bundling the data and a
        ${h.external_link("http://en.wikipedia.org/wiki/README", label="README")}
        file.
    </p>
</div>
% endif
