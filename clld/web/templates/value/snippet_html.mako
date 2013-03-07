
% if ctx.valueset.references:
<h4>${_('References')}</h4>
<p>${h.linked_references(request, ctx.valueset)|n}</p>
% endif

% if ctx.sentence_assocs:
<h4>${_('Sentences')}</h4>
<ol>
    % for a in ctx.sentence_assocs:
    <li>
        % if a.description:
        <p>${a.description}</p>
        % endif
        ${h.rendered_sentence(a.sentence)}
        % if a.sentence.references:
        <p>See ${h.linked_references(request, a.sentence)|n}</p>
        % endif
    </li>
    % endfor
</ol>
<script>
$(document).ready(function() {
    $('.ttip').tooltip({placement: 'bottom', delay: {hide: 300}});
});
</script>
% endif

% if not ctx.valueset.references and not ctx.sentence_assocs:
<p>No details available</p>
% endif
