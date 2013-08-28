<%! from json import dumps %>
##
##
##
<%def name="contextnavitem(route, label=None)">
    <li class="${'active' if request.matched_route.name == route else ''}">
        <a href="${request.route_url(route)}">${label or route.capitalize()}</a>
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
            <a class="accordion-toggle" data-toggle="collapse" data-parent="#${parent}" href="#${eid}">
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
    <% _options = {'aaSorting': [], 'bLengthChange': False, 'bPaginate': False, 'bInfo': False, 'sDom': 'fr<"toolbar">tip'} %>
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
        $('#${eid}').dataTable(${dumps(_options)|n});
    });
    </script>
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
##
##
<%def name="feed(title, url, eid='feed')">
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
    ${h.JSFeed.init(dict(eid=eid, url=url, title=title))|n}
});
        </script>
    </%self:well>
</%def>

##
## format history of an object
##
<%def name="history(obj_)">
    <% versions = obj_.history().all() %>
    % if versions:
    <%self:well title="History">
        <table>
            <tbody>
                <tr>
                    <td>${str(obj_.updated).split(' ')[0]}</td>
                    <td>${caller.body(item=obj_)}</td>
                </tr>
                % for v in versions:
                <tr>
                    <td>${str(v.updated).split(' ')[0]}</td>
                    <td>${caller.body(item=v)}</td>
                </tr>
                % endfor
            </tbody>
        </table>
    </%self:well>
    % endif
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
            <p>Coordinates: ${lang.latitude}, ${lang.longitude}</p>
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
        <%self:accordion_group eid="acc-names" parent="sidebar-accordion" title="Alternative names">
            <dl>
            % for type_, identifiers in h.groupby(sorted(lang.identifiers, key=lambda i: i.type), lambda j: j.type):
                <dt>${type_}:</dt>
                % for identifier in identifiers:
                <dd>${h.language_identifier(request, identifier)}</dd>
                % endfor
            % endfor
            </dl>
        </%self:accordion_group>
    </div>
</%def>

##
## language meta-information
##
<%def name="gbs_links(ids)">
    <script src="http://books.google.com/books?jscmd=viewapi&bibkeys=${','.join(ids)}&callback=CLLD.process_gbs_info">
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
