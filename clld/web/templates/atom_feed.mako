<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>${title}</title>
    <link href="${url}"/>
    <id>${url}</id>
    % for item in entries:
    <entry>
        <title>${item['title']}</title>
        <link href="${item['link']}"/>
        <id>${item['link']}</id>
        <updated>${item['updated']}</updated>
        <summary>${item['summary']}</summary>
    </entry>
    % endfor
</feed>
