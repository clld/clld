<%namespace name="util" file="../util.mako"/>

% if ctx.valueset.description:
<p>${h.text2html(ctx.valueset.description)}</p>
% endif

% if ctx.sentence_assocs:
${util.sentences(ctx, fmt='short')}
% endif

% if not ctx.sentence_assocs and not ctx.valueset.description:
<p>No details available</p>
% endif
