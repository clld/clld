<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "sources" %>



<h2>${_('Source')} ${ctx.name}</h2>

##
## TODO: the approach below doesn't scale to list citing objects. Need a DataTable!?
##
<ul class="nav nav-pills">
    % for attr in ['value', 'sentence', 'contribution']:
    % if getattr(ctx, attr + 'references'):
    <li class="dropdown">
        <a class="dropdown-toggle"
            data-toggle="dropdown"
            href="#">
            ${attr.capitalize()}s
            <b class="caret"></b>
        </a>
        <ul class="dropdown-menu">
            % for ref in getattr(ctx, attr + 'references'):
            <li>${h.link(request, getattr(ref, attr))}</li>
            % endfor
        </ul>
    </li>
    % endif
    % endfor
</ul>

<ol>
% for k, v in ctx.datadict().items():
<dt>${k}</dt>
<dd>${v}</dd>
% endfor
</ol>
