% if not 'multiple' in obj.options and obj.collection:
<select name="${obj.name}" data-placeholder="select ${obj.name}" id="${obj.eid}" class="${obj.options.get('class', '')}">
% for item in obj.collection:
    <option value="${item.id}">${getattr(item, 'label', item)}</option>
% endfor
</select>
% else:
<input type="hidden" name="${obj.name}" id="${obj.eid}" class="${obj.options.get('class', '')}"/>
% endif
<script type="text/javascript">
    $(document).ready(function() {
        $("#${obj.eid}").select2(${h.dumps(obj.options)|n});
        $("#${obj.eid}").select2('data', ${h.dumps(map(obj.format_result, obj.selected or []))|n});
    });
</script>
