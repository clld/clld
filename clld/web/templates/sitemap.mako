<?xml version="1.0" encoding="UTF-8"?>
<% from functools import partial; url = partial(request.route_url, request.matched_route.name.split('_')[0][:-1]) %>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
% for item in ctx.get_query(limit=50000):
    <url>
        <loc>${url(id=item.id)}</loc>
        <lastmod>${str(item.updated).split(' ')[0]}</lastmod>
   </url>
% endfor
</urlset>
