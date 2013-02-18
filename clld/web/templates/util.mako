
<%def name="data(obj=None)">
    <% obj = obj or ctx %>
    % if obj.data:
    <dl>
	% for key, items in h.groupby(sorted(obj.data, key=lambda o: (o.ord, o.key)), lambda x: x.key):
	    % if not key.startswith('_'):  ## we respect a convention to mark "private" data
	    <dt>${key}</dt>
	        % for item in items:
	        <dd>${item.value}</dd>
	        % endfor
	    % endif
        % endfor
    </dl>
    % endif
</%def>

<%def name="files(obj=None)">
    <% obj = obj or ctx %>
    % if obj.files:
    <dl>
	% for key, items in h.groupby(sorted(obj.files, key=lambda o: (o.ord, o.name)), lambda x: x.name):
	    % if not key.startswith('_'):  ## we respect a convention to mark "private" data
	    <dt>${key}</dt>
	        % for item in items:
	        <dd>${item.file.name}</dd>  ## TODO: link to associated file!
	        % endfor
	    % endif
        % endfor
    </dl>
    % endif
</%def>

<%def name="tree_node_label(level, id, checked=True)">
    <input class="level${level} treeview" type="checkbox" id="${id}"${' checked="checked"' if checked else ''}>
    <label for="${id}">
	<i class="icon-chevron-${'down' if checked else 'right'}"> </i>
	${caller.body()}
    </label>
</%def>

<%def name="accordion_group(eid, parent, title, open=False)">
    <div class="accordion-group">
        <div class="accordion-heading">
            <a class="accordion-toggle" data-toggle="collapse" data-parent="#${parent}" href="#${eid}">
                ${title}
            </a>
        </div>
        <div id="${eid}" class="accordion-body collapse${' in' if open else ''}">
            <div class="accordion-inner">
                ${caller.body()}
            </div>
        </div>
    </div>
</%def>
