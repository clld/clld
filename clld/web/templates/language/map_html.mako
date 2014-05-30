<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>
<%block name="title">${_('Languages')}</%block>

<h2>${_('Languages')}</h2>

${map.render()}

<div id="list-container" class="row-fluid">
    % for langs in h.partitioned(languages, n=4):
    <div class="span3">
        <table class="table table-condensed table-nonfluid">
            <tbody>
                % for language in langs:
                <tr>
                    <td><input title="check to display marker on map" type="checkbox" class="marker-toggle" id="marker-toggle-${language.id}" checked="checked"/></td>
                    <td>${h.link_to_map(language)}</td>
                    <td>${h.link(request, language)}</td>
                </tr>
                % endfor
            </tbody>
        </table>
    </div>
    % endfor
</div>
<script>
    $(window).load(function() {
        $('.marker-toggle').click(function(e) {
            CLLD.mapToggleLanguages('${map.eid}');
            e.stopPropagation();
        });
    });
</script>