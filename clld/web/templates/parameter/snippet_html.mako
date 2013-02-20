<%namespace name="util" file="../util.mako"/>

% if ctx.description:
<p>
    ${ctx.description}
</p>
% endif

% if ctx.domain:
<% total = 0 %>
<table class="table table-hover domain" style="width: auto;">
    <thead>
        <tr>
            <th>Value</th><th>Representation</th>
        </tr>
    </thead>
    <tbody>
        % for de in ctx.domain:
        <tr>
            <% total += len(de.values) %>
            <td>${de.name}</td><td style="text-align: right;">${len(de.values)}</td>
        </tr>
        % endfor
        <tr>
            <td><b>Total:</b></td><td style="text-align: right;">${total}</td>
        </tr>
    </tbody>
</table>
% endif
