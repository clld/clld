
<%def name="contextnav(*items)">
    <ul class="nav nav-pills">
        % for anchor, active in reversed(list(items)):
        <li class="pull-right${' active' if active else ''}">${anchor}</li>
        % endfor
    </ul>
</%def>

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
