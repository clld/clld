<%inherit file="home_comp.mako"/>

<h3>Downloads</h3>

<div class="span5 well well-small">
    <ul class="nav nav-tabs nav-stacked">
    % for name, dl in request.registry.getUtilitiesFor(h.interfaces.IDownload):
        <li><a href="${dl.url(request)}">${getattr(dl, 'description', dl.name)}</a></li>
    % endfor
    </ul>
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
