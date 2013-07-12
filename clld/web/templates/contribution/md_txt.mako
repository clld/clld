${', '.join(c.name for c in list(ctx.primary_contributors) + list(ctx.secondary_contributors))}. ${ctx.updated.year}. ${getattr(ctx, 'citation_name', ctx.__unicode__())}.
In: ${request.dataset.formatted_editors()} (eds.)
${request.dataset.description}.
${request.dataset.publisher_place}: ${request.dataset.publisher_name}.
(Available online at http://${request.dataset.domain}${request.resource_path(ctx)}, Accessed on ${h.datetime.date.today()}.)
