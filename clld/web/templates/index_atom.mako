<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>${ctx}</title>
    <link href="${request.url}"/>
    <updated>${h.datetime.datetime.now().isoformat()}</updated>
    <author>${request.dataset.name}</author>
    <id>${request.url}</id>
    % for item in ctx.get_query(limit=1000, undefer_cols=['updated']):
    <entry>
        <title>${item}</title>
        <link href="${request.resource_url(item)}"/>
        <id>${request.resource_url(item)}</id>
        <updated>${item.updated.isoformat()}</updated>
        % if item.description:
        <summary>${item.description}</summary>
        % endif
    </entry>
    % endfor
</feed>
