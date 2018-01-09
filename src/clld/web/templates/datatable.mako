<table id="${obj.eid}" cellpadding="0" cellspacing="0" border="0" class="table table-bordered order-column compact stripe">
    <thead>
        <tr>
            % for col in obj.cols:
            <th>${col.js_args['sTitle']}</th>
            % endfor
        </tr>
    </thead>
    <thead>
        <tr>
            % for col in obj.cols:
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
                            <input type="text" name="${col.name}" id="dt-filter-${col.name}" value="" placeholder="Search" class="input-${getattr(col, 'input_size', 'small')} control" />
                        % endif
                    % else:
                        <input type="text" name="${col.name}" id="dt-filter-${col.name}" value="" class="search_init control" style="display: none;"/>
                    % endif
                </th>
            % endfor
        </tr>
    </thead>
    <tbody>
    </tbody>
</table>
<script>
$(document).ready(function() {
    ${h.JSDataTable.init(obj.eid, obj.toolbar(), obj.options)|n};
});
</script>
