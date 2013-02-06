<%namespace name="util" file="../util.mako"/>

% if request.params.get('parameter'):
## called for the info windows on parameter maps
<% values = h.DBSession.query(h.models.Value).filter(h.models.Value.parameter_pk == int(request.params['parameter'])).filter(h.models.Value.language_pk == ctx.pk) %>
<h3>${h.link(request, ctx)}</h3>
<h4>Values</h4>
<ul class='unstyled'>
    % for value in values:
    <li>
        % if value.domainelement:
        ${value.domainelement.name}
        % else:
        ${value.name}
        % endif
        % if value.references:
            % for i, ref in enumerate(value.references):
            ${', ' if i > 0 else ''}
            ${h.link(request, ref.source)}
            ${'(' + ref.description + ')' if ref.description else ''}
            % endfor
        % endif
    </li>
    % endfor
</ul>
% else:

<h3>${h.link(request, ctx)}</h3>
% endif
