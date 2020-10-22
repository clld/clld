<!DOCTYPE html>
<html lang="en">
    <% from clld.interfaces import IMenuItems %>
    <%! active_menu_item = "dataset" %>
    <head>
        <meta charset="utf-8">
        <title>
            ${request.dataset.name} -
            <%block name="title"> </%block>
        </title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="">
        <meta name="author" content="">
        <link rel="shortcut icon"
              href="${request.static_url(request.registry.settings['clld.favicon'], _query=dict(v=request.registry.settings['clld.favicon_hash']))}"
              type="image/x-icon" />

        % for asset in assets['css'].urls():
        <link href="${request.static_url(asset[1:])}" rel="stylesheet">
        % endfor

        % if request.registry.settings.get('clld.environment') == 'production':
        <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>

        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <script src="https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/Leaflet.fullscreen.min.js"></script>
        <link href="https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/leaflet.fullscreen.css" rel="stylesheet" />
        % endif

        % for asset in assets['js'].urls():
        <script src="${request.static_url(asset[1:])}"></script>
        % endfor

        <link rel="unapi-server" type="application/xml" title="unAPI" href="${request.route_url('unapi')}">
        <script src="${request.route_url('_js', _query=request.query_params)}"></script>
        <%block name="head"> </%block>
        % for name, util in request.registry.getUtilitiesFor(h.interfaces.IStaticResource):
            % if util.type == 'css':
            <link href="${request.static_url(util.asset_spec)}" rel="stylesheet">
            % elif util.type == 'js':
            <script src="${request.static_url(util.asset_spec)}"></script>
            % endif
        % endfor
    </head>
    <body id="r-${request.matched_route.name if request.matched_route else 'body'}">
        <%block name="header"></%block>

        <div id="top" class="navbar navbar-static-top${' navbar-inverse' if request.registry.settings.get('navbar.inverse') else ''}">
            <div class="navbar-inner">
                <div class="container-fluid">
                    <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </a>
                    <%block name="brand"> </%block>
                    <div class="nav-collapse collapse">
                        <ul class="nav">
                        % for name, item in request.registry.getUtility(IMenuItems).items():
                        <% href, title = item(context.get('ctx'), request) %>
                            <li id="menuitem_${name}" class="${'active' if name == self.attr.active_menu_item else ''}">
                                <a href="${href}" title="${title}">${title}</a>
                            </li>
                        % endfor
                        </ul>
                    <%block name="navextra"></%block>
                    </div><!--/.nav-collapse -->
                </div>
            </div>
        </div>
        % if hasattr(self, 'contextnav'):
        <div id="contextnavbar" class="navbar navbar-static-top${' navbar-inverse' if request.registry.settings.get('navbar.inverse') else ''}">
            <div class="navbar-inner">
                <div class="container-fluid">
                    <a class="btn btn-navbar" data-toggle="collapse" data-target="#second">
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </a>
                    <div id="second" class="nav-collapse collapse">
                        <ul class="nav pull-right">
                            ${self.contextnav()}
                        </ul>
                    </div><!--/.nav-collapse -->
                </div>
            </div>
        </div>
        % endif

        <div class="container-fluid">
            % if ctx and getattr(ctx, 'metadata', None):
            <abbr class="unapi-id" title="${h.urlescape(request.resource_url(ctx))}"></abbr>
            % endif
            % if not getattr(self.attr, 'multirow', False):
                <div class="row-fluid">
                % if hasattr(self, 'sidebar'):
                    <div class="span8">
                    ${next.body()}
                    </div>
                    <div id="sidebar" class="span4">
                        ${self.sidebar()}
                    </div>
                % else:
                    <div class="span12">
                    ${next.body()}
                    </div>
                % endif
                </div>
                % if hasattr(self, 'below_sidebar'):
                <div class="row-fluid">
                    <div class="span12">
                    ${self.below_sidebar()}
                    </div>
                </div>
                % endif
            % else:
                ${next.body()}
            % endif
            <div class="row-fluid">
                <div class="span12">
                <footer>
                <%block name="footer">
                    <div class="row-fluid" style="padding-top: 15px; border-top: 1px solid black;">
                        <div class="span3">
                            <a href="${request.dataset.publisher_url}"
                               title="${request.dataset.publisher_name}, ${request.dataset.publisher_place}">
                            % if request.registry.settings.get('clld.publisher_logo'):
                                <img width="80" src="${request.static_url(request.registry.settings['clld.publisher_logo'])}" />
                            % else:
                                ${request.dataset.publisher_name}, ${request.dataset.publisher_place}
                            % endif
                            </a>
                        </div>
                        <div class="span6" style="text-align: center;">
                            <% license_icon = h.format_license_icon_url(request) %>
                            % if license_icon:
                            <a rel="license" href="${request.dataset.license}">
                                <img alt="License" style="border-width:0" src="${license_icon}" />
                            </a>
                            <br />
                            % endif
                            <%block name="footer_citation">
                            ${request.dataset.formatted_name()}
                            edited by
                            <span xmlns:cc="https://creativecommons.org/ns#"
                                  property="cc:attributionName"
                                  rel="cc:attributionURL">
                                ${request.dataset.formatted_editors()}
                           </span>
                            </%block>
                            <br />
                            is licensed under a
                            <a rel="license" href="${request.dataset.license}">
                                ${request.dataset.jsondata.get('license_name', request.dataset.license)}</a>.
                        </div>
                        <div class="span3" style="text-align: right;">
                            % if request.registry.settings.get('clld.privacy_policy_url'):
                                <a class="clld-privacy-policy" href="${request.registry.settings['clld.privacy_policy_url']}">${_('Privacy Policy')}</a><br/>
                            % endif
                            <a class="clld-disclaimer" href="${request.route_url('legal')}">${_('Disclaimer')}</a>
                            <br/>
                            % if request.registry.settings.get('clld.github_repos'):
                            <a href="https://github.com/${request.registry.settings['clld.github_repos']}">
                                <i class="icon-share">&nbsp;</i>
                                Application source
                                % if request.registry.settings['clld.git_tag']:
                                    (${request.registry.settings['clld.git_tag']})
                                % endif
                                on<br/>
                                <img height="25" src="${request.static_url('clld:web/static/images/GitHub_Logo.png')}" />
                            </a>
                            % endif
                        </div>
                    </div>
                </%block>
                </footer>
                </div>
            </div>
        </div>

        <div id="Modal" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="ModalLabel" aria-hidden="true">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h3 id="ModalLabel"></h3>
            </div>
            <div id="ModalBody" class="modal-body">
            </div>
        </div>

        <script>
            <%block name="javascript"> </%block>
        </script>
    </body>
</html>
