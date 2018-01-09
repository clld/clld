<%inherit file="../snippet.mako"/>
<%namespace name="util" file="../util.mako"/>

% if ctx.description:
<p>${h.text2html(ctx.description)}</p>
% endif

<h3>${_('Values')}</h3>
<ul class="unstyled">
% for value in ctx.values:
<li>
${h.link(request, value)}${h.format_frequency(request, value)}
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
</li>
% endfor
</ul>
