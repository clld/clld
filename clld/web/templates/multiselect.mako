% if multiselect.collection:
<select name="${multiselect.name}" multiple data-placeholder="select ${multiselect.name}" id="${multiselect.eid}">
% for item in multiselect.collection:
    <option value="${item.id}">${item}</option>
% endfor
</select>
% else:
<input type="hidden" name="${multiselect.name}" id="${multiselect.eid}"/>
% endif
<script type="text/javascript">
    $(document).ready(function() {
        $("#${multiselect.eid}").select2(${h.dumps(multiselect.options)|n});
        $("#${multiselect.eid}").select2('data', ${h.dumps(map(multiselect.format_result, selected))|n});
    });
</script>
