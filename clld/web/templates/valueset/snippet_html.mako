<%namespace name="util" file="../util.mako"/>

% if ctx.description:
<p>${h.text2html(ctx.description)}</p>
% endif

<h3>${_('Values')}</h3>
<ul class="unstyled">
% for value in ctx.values:
<li>
${h.link(request, value)}${h.format_frequency_and_confidence(value)}
% if value.confidence:
<dl>
    <dt>${_('Confidence')}:</dt>
    <dd>${value.confidence}</dd>
</dl>
% endif
% if value.sentence_assocs:
<h4>${_('Sentences')}</h4>
${util.sentences(value)}
% endif

% if not ctx.references and not ctx.sentence_assocs:
<p>No details available</p>
% endif
</li>
% endfor
</ul>
