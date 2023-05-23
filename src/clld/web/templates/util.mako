<%! from json import dumps %>
<%! from clldutils.misc import slug %>
<%! from clld.web.util import doi %>
<%! from clld.web.icon import Icon %>
##
##
##
<%def name="contextnavitem(route, label=None)">
    <li class="${'active' if request.matched_route.name == route else ''}">
        <a href="${request.route_url(route)}">${label or _(route.capitalize())}</a>
    </li>
</%def>

##
## format the key-value pairs from resources with data as dl items
##
<%def name="data(obj=None, with_dl=True)">
    <% obj = obj or ctx %>
    % if obj.data:
    %if with_dl:
    <dl>
    % endif
        % for key, items in h.groupby(sorted(obj.data, key=lambda o: (o.ord, o.key)), lambda x: x.key):
            % if not key.startswith('_'):  ## we respect a convention to mark "private" data
            <dt>${key}</dt>
                % for item in items:
                <dd>${item.value}</dd>
                % endfor
            % endif
        % endfor
    %if with_dl:
    </dl>
    % endif
    % endif
</%def>

##
## format files associated with a resource
##
<%def name="files(obj=None)">
    <% obj = obj or ctx %>
    % if obj.files:
    <dl>
        % for key, items in h.groupby(sorted(obj.files, key=lambda o: (o.ord, o.name)), lambda x: x.name):
            % if not key.startswith('_'):
            <dt>${key}</dt>
                % for item in items:
                <dd>${h.link(request, item.file)}</dd>
                % endfor
            % endif
        % endfor
    </dl>
    % endif
</%def>

##
## format the label of a tree node in a css-only tree control
##
<%def name="tree_node_label(level, id, checked=True)">
    <input class="level${level} treeview" type="checkbox" id="${id}"${' checked="checked"' if checked else ''}>
    <label for="${id}">
        <i class="icon-treeview icon-chevron-${'down' if checked else 'right'}"> </i>
        ${caller.body()}
    </label>
</%def>

##
## format a group within a bootstrap accordion
##
<%def name="accordion_group(eid, parent, title=None, open=False)">
    <div class="accordion-group">
        <div class="accordion-heading">
            <a class="accordion-toggle" data-toggle="collapse" data-parent="#${parent}" href="#${eid}" title="${'click to hide or show {0}'.format(title or '')}">
                ${title or caller.title()}
            </a>
        </div>
        <div id="${eid}" class="accordion-body collapse${' in' if open else ''}">
            <div class="accordion-inner">
                ${caller.body()}
            </div>
        </div>
    </div>
</%def>

##
##
##
<%def name="stacked_links(items)">
    <ul class="nav nav-pills nav-stacked">
    % for item in items:
        <li>${h.link(request, item)}</li>
    % endfor
    </ul>
</%def>

##
## format an HTML table, enhanced via jQuery DataTables
##
<%def name="table(items, eid='table', class_='table-hover', options=None)">
    ##<% _options = {'aaSorting': [], 'bLengthChange': False, 'bPaginate': False, 'bInfo': False, 'sDom': 'fr<"toolbar">tip'} %>
    <% _options = {'aaSorting': [], 'bLengthChange': True, 'bPaginate': False, 'bInfo': False, 'sDom': 'fr<"toolbar">tip'} %>
    <% _options.update(options or {}) %>
    <table id="${eid}" class="standard table ${class_}">
        <thead>
            <tr>${caller.head()}</tr>
        </thead>
        <tbody>
            % for item in items:
            <tr>${caller.body(item=item)}</tr>
            % endfor
        </tbody>
        % if hasattr(caller, 'foot'):
        <tfoot>
            <tr>${caller.foot()}</tr>
        </tfoot>
        % endif
    </table>
    <script>
    $(document).ready(function() {
        ##$('#${eid}').dataTable({aaSorting: [], bLengthChange: false, bPaginate: false, bInfo: false, sDom: 'fr<"toolbar">tip'});
        CLLD.DataTables['${eid}'] = $('#${eid}').dataTable(${dumps(_options)|n});

        $(document).on('click', '#${eid} tbody td button.details', function () {
            var nTr = $(this).parents('tr')[0];
            if (CLLD.DataTables['${eid}'].fnIsOpen(nTr)) {
                CLLD.DataTables['${eid}'].fnClose(nTr);
            } else {
                $.get($(this).attr('href'), {}, function(data, textStatus, jqXHR) {
                    CLLD.DataTables['${eid}'].fnOpen(nTr, data, 'details');
                }, 'html');
            }
        });
    });
    </script>
</%def>

##
## format a list of key-value pairs as HTML table
##
<%def name="dl_table(*items, **kw)">
    <table class="table table-condensed table-nonfluid">
        <tbody>
            % for key, value in items:
            <tr><td class="key">${key}:</td><td>${value}</td></tr>
            % endfor
            % for key, value in kw.items():
            <tr><td class="key">${key}:</td><td>${value}</td></tr>
            % endfor
        </tbody>
    </table>
</%def>

##
## format a div of class well
##
<%def name="well(title=None, paragraphs=None)">
    <div class="well well-small">
        % if title:
        <h3>${title}</h3>
        % endif
        % if hasattr(caller, 'body'):
            ${caller.body()}
        % endif
        % for p in (paragraphs or '').split('\n'):
            <p>${p}</p>
        % endfor
    </div>
</%def>

##
## format citation information as well.
##
<%def name="cite(obj=None, title='Cite')">
    <%self:well title="${title}">
        ${h.newline2br(h.text_citation(request, obj or ctx))|n}
        ${h.cite_button(request, obj or ctx)}
    </%self:well>
</%def>

##
##
##
<%def name="feed(title, url, eid='feed', **kw)">
    <%self:well>
        <div id="${eid}">
        % if hasattr(caller, 'body'):
            ${caller.body()}
        % else:
            No items.
        % endif
        </div>
        <script>
$(document).ready(function() {
    ${h.JSFeed.init(dict(eid=eid, url=url, title=title, **kw))|n}
});
        </script>
    </%self:well>
</%def>

##
## format the sentences associated with a Value instance
##
<%def name="sentences(obj=None, fmt='long')">
    <% obj = obj or ctx %>
    <dl id="sentences-${obj.pk}">
        % for a in obj.sentence_assocs:
        <dt>${h.link(request, a.sentence, label='%s %s:' % (_('Sentence'), a.sentence.id))}</dt>
        <dd>
            % if a.description and fmt == 'long':
            <p>${a.description}</p>
            % endif
            ${h.rendered_sentence(a.sentence, fmt=fmt)}
            % if a.sentence.audio:
            <div>
                <audio controls="controls">
                    <source src="${request.file_url(a.sentence.audio)}"/>
                </audio>
            </div>
            % endif
            % if a.sentence.references and fmt == 'long':
            <p>Source: ${h.linked_references(request, a.sentence)|n}</p>
            % endif
        </dd>
        % endfor
    </dl>
</%def>

##
## language meta-information
##
<%def name="language_meta(lang=None)">
    <% lang = lang or ctx %>
    <div class="accordion" id="sidebar-accordion">
        % if getattr(request, 'map', False):
        <%self:accordion_group eid="acc-map" parent="sidebar-accordion" title="Map" open="${True}">
            ${request.map.render()}
            ${h.format_coordinates(lang)}
        </%self:accordion_group>
        % endif
        % if lang.sources:
        <%self:accordion_group eid="sources" parent="sidebar-accordion" title="Sources">
            <ul>
                % for source in lang.sources:
                <li>${h.link(request, source, label=source.description)}<br />
                <small>${h.link(request, source)}</small></li>
                % endfor
            </ul>
        </%self:accordion_group>
        % endif
	% if lang.identifiers:
        <%self:accordion_group eid="acc-names" parent="sidebar-accordion" title="${_('Alternative names')}">
            <dl>
            % for type_, identifiers in h.groupby(sorted(lang.identifiers, key=lambda i: i.type), lambda j: j.type):
                <dt>${type_}:</dt>
                % for identifier in identifiers:
                <dd>${h.language_identifier(request, identifier)}</dd>
                % endfor
            % endfor
            </dl>
        </%self:accordion_group>
	% endif
    </div>
</%def>

##
##
##
<%def name="gbs_links(ids)">
    <script src="https://books.google.com/books?jscmd=viewapi&bibkeys=${','.join(ids)}&callback=CLLD.process_gbs_info">
    </script>
</%def>

##
##
##
<%def name="md_tab_li(_format, route, title)">
    <% url = request.route_url(route + '_alt', id=ctx.id, ext='md.html', _query=dict(format=_format)) %>
    <li class="${'active' if format == _format else ''}">
        <a id='tab-opener-${_format}' onclick='${h.JSModal.show(ctx.name.replace("'", ""), url)|n}; return false' href='#'>${title}</a>
    </li>
</%def>


<%def name="md_tabs()">
    <% format = request.params.get('format', 'md.txt') %>
    <% adapters = dict((a.extension, a) for n, a in h.get_adapters(h.interfaces.IMetadata, ctx, request)) %>

    <ul class="nav nav-tabs">
    % for fmt in ['md.txt', 'md.bib', 'md.ris']:
        % if fmt in adapters:
        <li class="${'active' if format == fmt else ''}">
            <a id='md-tab-opener-${fmt}'
               onclick='${h.JSModal.show(ctx.name.replace("'", ""), request.resource_url(ctx, ext='md.html', _query=dict(format=fmt)))|n}; return false'
               href='#'>${adapters[fmt].label}</a>
        </li>
        % endif
    % endfor
    </ul>

    % if format == 'md.txt':
    <blockquote>
    ${h.text2html(adapters[format].render(ctx, request))|n}
    </blockquote>
    % else:
    <pre>${adapters[format].render(ctx, request)}</pre>
    % endif
</%def>

##
##
##
<%def name="values_and_sentences(parameter=None, values_dt=None)">
    <div id="list-container">
    <% parameter = parameter or ctx %>
    <div class="tabbable">
	<ul class="nav nav-tabs">
	    <li class="active"><a href="#tab1" data-toggle="tab">${_('Values')}</a></li>
	    <li><a href="#tab2" data-toggle="tab">${_('Sentences')}</a></li>
	</ul>
	<div class="tab-content" style="overflow: visible;">
	    <div id="tab1" class="tab-pane active">
		${(values_dt or request.get_datatable('values', h.models.Value, parameter=parameter)).render()}
	    </div>
	    <div id="tab2" class="tab-pane">
		${request.get_datatable('sentences', h.models.Sentence, parameter=parameter).render()}
	    </div>
	</div>
    </div>
    </div>
</%def>

##
##
##
<%def name="sources_list(sources)">
    <dl>
        % for source in sources:
        <dt style="clear: right;">${h.link(request, source)}</dt>
        <dd id="${h.format_gbs_identifier(source)}">${source.description}</dd>
        % endfor
    </dl>
    ${self.gbs_links(filter(None, [s.gbs_identifier for s in sources]))}
</%def>

##
##
##
<%def name="codes(lang=None, style='pull-right')">
    <% lang = lang or ctx %>
    <ul class="inline codes ${style}">
        % for type_ in [h.models.IdentifierType.glottolog, h.models.IdentifierType.iso]:
            <% codes = lang.get_identifier_objs(type_) %>
            % if len(codes) == 1:
            <li>
                <span class="large label label-info">
                    ${type_.description}:
                    ${h.language_identifier(request, codes[0], inverted=True, style="color: white;")}
                </span>
            </li>
            % endif
        % endfor
    </ul>
</%def>

###
### section
###
<%def name="section(title=None, level=3, id=None, prefix='sec-')">
    <% id = id or prefix + slug(title or 'none') %>
    <div class="section" id="${id}">
        <h${level}>
            % if title:
            ${title}
            % elif hasattr(caller, 'title'):
            ${caller.title()}
            % endif
            <a href="#top" title="go to top of the page" style="vertical-align: bottom">&#x21eb;</a>
            <a class="headerlink" href="#${id}" title="Permalink to this headline">¶</a>
        </h${level}>
        ${caller.body()}
    </div>
</%def>

###
### head content necessary to use coloris color picker functionality.
###
<%def name="head_coloris()">
<link rel="stylesheet" href="${req.static_url('clld:web/static/css/coloris.min.css')}"/>
<script src="${req.static_url('clld:web/static/js/coloris.min.js')}"></script>
<style>
    input.coloris {width: 20px; height: 20px;}
    .clr-field button {
        width: 100%;
        height: 100%;
        border-radius: 5px;
        cursor: pointer !important;
    }
    #clr-picker {
        z-index: 10000;
    }
    select.shape {
        margin-right: 5px;
        margin-top: 0 !important;
        margin-bottom: 2px;
    }
</style>
</%def>


<%def name="coloris_icon_picker(icon)">
    <input title="Click to choose marker color" class="coloris" id="${icon.select_id}-c" type="text" data-coloris value="${icon.color}" style="cursor: pointer;">
    <select title="Select marker shape" class="shape" id="${icon.select_id}-s" style="width: 45px; margin-top: 10px">
    % for shape, glyph in [('s', '\u25a0'), ('d', '\u25c6'), ('c', '\u25cf'), ('t', '\u25b2'), ('f', '\u25bc')]:
        <option value="${shape}" style="font-size: 30px;"${' selected' if shape == icon.shape else ''}>${glyph}</option>
    % endfor
    </select>
</%def>


<%def name="parameter_map_reloader(icons)">
    <% quoted = lambda s: '"{}"'.format(s) %>
    <a class="btn" onclick='CLLD.reload_map([${", ".join(quoted(icon.select_id) for icon in icons)|n}])'>reload</a>
</%def>

<%def name="combination_valuetable(ctx, iconselect=False)">
    <%self:table items="${enumerate(ctx.domain)}" args="item" eid="refs" class_="table-condensed table-striped table-nonfluid" options="${dict(aaSorting=[[2, 'desc']])}">\
        <%def name="head()">
            <th> </th>
            <th> </th>
            <th>${' / '.join(h.link(request, p) for p in ctx.parameters)|n}</th>
            <th>Number of languages</th>
        </%def>
        <td>
            % if item[1].languages:
            <button title="click to toggle display of languages for value ${item[1].name}"
                    type="button" class="btn btn-mini expand-collapse" data-toggle="collapse" data-target="#de-${item[0]}">
                <i class="icon icon-plus"> </i>
            </button>
            % endif
        </td>
        <td>
            % if item[1].languages:
                % if iconselect:
                ${coloris_icon_picker(Icon.from_req(item[1], req))|n}
                ${parameter_map_reloader([Icon.from_req(de, req) for de in ctx.domain])|n}
                % else:
                <img height="20" width="20" src="${item[1].icon.url(request)}"/>
                % endif
            % endif
        </td>
        <td>
            ${item[1].name}
            <div id="de-${item[0]}" class="collapse">
                <table class="table table-condensed table-nonfluid">
                    <tbody>
                        % for language in item[1].languages:
                        <tr>
                            <td>${h.link_to_map(language)}</td>
                            <td>${h.link(request, language)}</td>
                        </tr>
                        % endfor
                    </tbody>
                </table>
            </div>
        </td>
        <td style="text-align: right;">${str(len(item[1].languages))}</td>
    </%self:table>
    % if iconselect:
    <script>
    $(document).ready(function() {
        $('.expand-collapse').click(function(){
            $(this).children('i').toggleClass('icon-minus icon-plus');
        });
    });
    </script>
    % endif
</%def>

##
## Download info for datasets archived with Zenodo.
## It uses the following data specified in the clld section of appconf.ini:
## - zenodo_concept_doi
## - zenodo_version_doi (optional)
## - zenodo_version_tag (optional)
## - dataset_github_repos
##
<%def name="dataset_download(div_class='alert alert-info', label=None)">
    <div class="${div_class}">
        <p>
            The ${label or req.dataset.name} web application serves
            % if req.registry.settings.get('clld.zenodo_version_tag'):
                version ${req.registry.settings['clld.zenodo_version_tag']}
                % if req.registry.settings.get('clld.zenodo_version_doi'):
                    ${doi.badge(req.registry.settings['clld.zenodo_version_doi'])}
                % endif
                ##
                ## FIXME: link to version doi if available!
                ##
            % elif req.registry.settings.get('clld.dataset_github_repos'):
                the latest
                ${h.external_link('https://github.com/{}/releases'.format(req.registry.settings['clld.dataset_github_repos']), label=_('released version'))}
            % else:
                a version
            % endif
            % if req.registry.settings.get('clld.dataset_github_repos'):
                of data curated at
                ${h.external_link('https://github.com/{}'.format(req.registry.settings['clld.dataset_github_repos']), label=req.registry.settings['clld.dataset_github_repos'])}.
            % else:
                of the dataset ${req.dataset.name}.
            % endif
            All released versions are accessible via
            ${doi.badge(req.registry.settings['clld.zenodo_concept_doi'])}
            <br/>
            on ${h.external_link('https://zenodo.org', label='Zenodo')} as well.
        </p>
    </div>
</%def>

<%def name="dataset_citation()">
    <blockquote>
        ${h.newline2br(h.get_adapter(h.interfaces.IRepresentation, req.dataset, req, ext='md.txt').render(ctx, request))|n}
    </blockquote>
</%def>
