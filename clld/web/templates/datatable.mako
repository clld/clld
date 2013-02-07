<table id="${datatable.eid}" cellpadding="0" cellspacing="0" border="0" class="table table-condensed table-bordered table-striped">
    <thead>
        <tr>
            % for col in datatable.cols:
            <th>${col.js_args['sTitle']}</th>
            % endfor
        </tr>
    </thead>
    <tbody>
        % if not datatable.server_side:
            % for item in datatable.get_query():
            <tr>
                % for col in datatable.cols:
                <td>${col.format(item)}</td>
                % endfor
            </tr>
            % endfor
        % endif
    </tbody>
    % if datatable.search:
    <tfoot>
	<tr>
            % for col in datatable.cols:
	    <th style="text-align: left;">
                % if col.js_args.get('bSearchable', True):
		    % if hasattr(col, 'choices'):
		    <select class="control" name="${col.name}">
			<option value="">--any--</option>
			% for val in getattr(col, 'choices'):
			<option value="${val}">${val}</option>
			% endfor
		    </select>
		    % else:
		    <input type="text" name="${col.name}" value="" placeholder="Search ${col.js_args['sTitle']}" class="input-small control" />
		    % endif
                % else:
                    <input type="text" name="${col.name}" value="" class="search_init control" style="display: none;"/>
                % endif
            </th>
            % endfor
	</tr>

    </tfoot>
    % endif
</table>
<script>
$(document).ready(function() {
    ${h.JSDataTable.init(datatable.eid, datatable.toolbar(), datatable.options)|n};
});
</script>
