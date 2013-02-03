<%namespace name="util" file="../util.mako"/>

% if ctx.description:
<p>
    ${ctx.description}
</p>
% endif

% if ctx.domain:
<table class="table" style="width: auto;">
    <tr>
        <th>Value</th><th>Representation</th>
    </tr>
    % for de in ctx.domain:
    <tr>
        <td>${de.name}</td><td style="text-align: right;">${len(de.values)}</td>
    % endfor
</table>
% endif
