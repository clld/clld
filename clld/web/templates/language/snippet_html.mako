<%namespace name="util" file="../util.mako"/>

% if request.params.get('parameter'):
## called for the info windows on parameter maps
<% valueset = h.DBSession.query(h.models.ValueSet).filter(h.models.ValueSet.parameter_pk == int(request.params['parameter'])).filter(h.models.ValueSet.language_pk == ctx.pk).first() %>
<h3>${h.link(request, ctx)}</h3>
% if valueset:
<h4>${_('Values')}</h4>
<ul class='unstyled'>
    % for value in valueset.values:
    <li>
        % if value.domainelement:
        ${value.domainelement.name}
        % else:
        ${value.name}
        % endif
        ##
        ## TODO: confidence, frequency
        ##
    </li>
    % endfor
</ul>
% if valueset.references:
<h4>${_('References')}</h4>
<p>${h.linked_references(request, valueset)}</p>
% endif
% endif
% else:
<h3>${h.link(request, ctx)}</h3>
% endif
