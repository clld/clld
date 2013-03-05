
% if ctx.description:
<p>${h.text2html(ctx.description)}</p>
% endif

<h3>${_('Values')}</h3>
<ul class="unstyled">
% for value in ctx.values:
<li>
${h.link(request, value)}
##
## TODO: frequency, confidence!
##
% if value.sentence_assocs:
<h4>${_('Sentences')}</h4>
<ol>
    % for a in value.sentence_assocs:
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

% if not ctx.references and not ctx.sentence_assocs:
<p>No details available</p>
% endif
</li>
% endfor
</ul>
