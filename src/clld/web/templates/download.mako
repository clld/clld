<%inherit file="home_comp.mako"/>

<h3>Downloads</h3>

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


## eWAVE serves the latest  released version of data curated at  cldf-datasets/ewave. All released versions are accessible via
## DOI
## on  Zenodo as well.

## Need: dataset repos; concept DOI
##<p>
##    <a href="${req.resource_url(req.dataset)}">eWAVE</a>
##    serves the latest
    ##   ${h.external_link('https://github.com/cldf-datasets/ewave/releases', label='released version')}
##    of data curated at
##    ${h.external_link('https://github.com/cldf-datasets/ewave', label='cldf-datasets/ewave')}.
##    All released versions are accessible via <br/>
##    <a href="https://doi.org/10.5281/zenodo.3603136">
##        <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.3603136.svg" alt="DOI">
##    </a>
##    <br/>
##    on
##    ${h.external_link('https://zenodo.org', label='Zenodo')}
##    as well.
##</p>
