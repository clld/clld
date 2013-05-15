<table id="${datatable.eid}" cellpadding="0" cellspacing="0" border="0" class="table table-condensed table-bordered table-striped">
    <thead>
        <tr>
            % for col in datatable.cols:
            <th>${col.js_args['sTitle']}</th>
            % endfor
        </tr>
    </thead>
    <tbody>
    </tbody>
    <tfoot>
	<tr>
            % for col in datatable.cols:
	    <th style="text-align: left;">
                % if col.js_args.get('bSearchable', True):
		    % if hasattr(col, 'choices'):
		    <select class="control input-${getattr(col, 'input_size', 'small')}" name="${col.name}" id="dt-filter-${col.name}">
			<option value="">--any--</option>
			% for val in getattr(col, 'choices'):
			    % if isinstance(val, tuple) and len(val) == 2:
			    <option value="${val[0]}">${val[1]}</option>
			    % else:
			    <option value="${val}">${val}</option>
			    % endif
			% endfor
		    </select>
		    % else:
		    <input type="text" name="${col.name}" id="dt-filter-${col.name}" value="" placeholder="Search ${col.js_args['sTitle']}" class="input-${getattr(col, 'input_size', 'small')} control" />
		    % endif
                % else:
                    <input type="text" name="${col.name}" id="dt-filter-${col.name}" value="" class="search_init control" style="display: none;"/>
                % endif
            </th>
            % endfor
	</tr>
    </tfoot>
</table>
<script>
$(document).ready(function() {
    ${h.JSDataTable.init(datatable.eid, datatable.toolbar(), datatable.options)|n};
});
</script>



##    CLLD.DataTable.init(
##    "Families",
##    "<div class=\"btn-group right\"><a class=\"btn dropdown-toggle\" data-toggle=\"dropdown\" href=\"#\"><i class=\"icon-download-alt\"></i><span class=\"caret\"></span></a><ul class=\"dropdown-menu\"><li><a href=\"#\" onclick=\"document.location.href = CLLD.DataTable.current_url(&#39;xls&#39;); return false;\">xls</a></li></ul><button class=\"btn-info btn\" id=\"cdOpener\" type=\"button\"><i class=\"icon-info-sign icon-white\"></i></button></div>", {"sDom": "<'dt-before-table row-fluid'<'span4'i><'span6'p><'span2'f<'dt-toolbar'>>r>t",
##    "aoColumns": [{"sTitle": "Name", "sName": "primaryname"}, {
##    "sDescription": "<dl><dt>North America</dt><dd>North and Middle America up to Panama. Includes Greenland. </dd><dt>South America</dt><dd>Everything South of Dari\u00e9n</dd><dt>Africa</dt><dd>The continent</dd><dt>Australia</dt><dd>The continent </dd><dt>Eurasia</dt><dd>The Eurasian landmass North of Sinai. Includes Japan and islands to the North of it. Does not include Insular South East Asia.</dd><dt>Pacific</dt><dd>All islands between Sumatra and the Americas, excluding islands off Australia and excluding Japan and islands to the North of it.</dd></dl>",
##    "sTitle": "Macro-area", "sName": "macro-area", "bSortable": false}, {"sTitle": "Sub-families", "sName": "child_family_count"}, {"sTitle": "Child languages", "sName": "child_language_count"}, {"sTitle": "Child dialects", "sName": "child_dialect_count"}], "sAjaxSource": "http://localhost:6543/glottolog/family", "sPaginationType": "bootstrap", "bProcessing": true, "bServerSide": true, "iDisplayLength": 100, "bAutoWidth": false, "aLengthMenu": [[50, 100, 200], [50, 100, 200]]});
