<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>

<%! from json import dumps %>
<%! from clld.interfaces import IDataTable %>
<%! from clld.db.models.common import Value %>

<h2>${_('Parameter')} ${ctx.name}</h2>

##
## TODO: replace by map.render()!
    ##<% m = request.registry.queryUtility(IMap, name='parameter'); m = m(request, ctx) %>
    ##% if m:
    ##    ${m.render()}
    ##% endif
##

<ul class="nav nav-pills">
    <li class="dropdown active pull-right">
        <a class="dropdown-toggle" data-toggle="dropdown" href="#">
        Toggle Values
        <b class="caret"></b>
        </a>
        <ul class="dropdown-menu">
            % for de in ctx.domain:
            <li onclick="CLLD.Map.layers['${de.name}'].display(!$(this.firstElementChild.firstElementChild).prop('checked')); $(this.firstElementChild.firstElementChild).prop('checked', !$(this.firstElementChild.firstElementChild).prop('checked'));">
                <label class="checkbox inline" style="margin-left: 5px; margin-right: 5px;">
                    <input type="checkbox" checked="checked">
                    ##
                    ## TODO: creation of legend must be pluggable!
                    ##
                    <img src="${request.static_url('wals3:static/icons/'+de.icon_id+'.png')}">
                    ${de.name}
                </label>
            </li>
            % endfor
        </ul>
    </li>
</ul>


<div id="map"> </div>

<div>
    <% dt = request.registry.getUtility(IDataTable, 'values'); dt = dt(request, Value, parameter=ctx) %>
    ${dt.render()}
</div>



<%block name="head">
    ${parent.head()}
    <style type="text/css">
        #map {
            width: 100%;
            height: 500px;
            border: 1px solid black;
        }
    </style>
</%block>


<%block name="javascript">
    ${parent.javascript()}
    $(function (){
        % if ctx.domain:
        CLLD.Map.init(${dumps([[de.name, request.route_url('parameter_alt', id=ctx.id, ext='geojson', _query=dict(domainelement=str(de.id)))] for de in ctx.domain])|n}, ${dumps({'style_map': 'wals_feature'})|n});
        % else:
        CLLD.Map.init(${dumps([[ctx.name, request.route_url('parameter_alt', id=ctx.id, ext='geojson')]])|n});
        % endif
    });
</%block>
