<!DOCTYPE html>
<html lang="en">
    <% from clld.interfaces import IMenuItems %>
    <%! active_menu_item = "a_home" %>
    <head>
        <meta charset="utf-8">
        <title>
            ${request.registry.settings.get('clld.publication.sitetitle_short', 'CLLD')}
            <%block name="title"> </%block>
        </title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="">
        <meta name="author" content="">

        <script type="text/javascript" src="https://www.google.com/jsapi"></script>
        <script type="text/javascript">
            google.load("feeds", "1");
        </script>

        <link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet-0.5/leaflet.css" />
        <!--[if lte IE 8]>
        <link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet-0.5/leaflet.ie.css" />
        <![endif]-->

        % for asset in assets['css'].urls():
        <link href="${request.static_url('clld:web/static' + asset)}" rel="stylesheet">
        % endfor

        % if request.registry.settings.get('clld.environment') == 'production':
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
        <script src="http://cdn.leafletjs.com/leaflet-0.5/leaflet.js"></script>
        % endif

        % for asset in assets['js'].urls():
        <script src="${request.static_url('clld:web/static' + asset)}"></script>
        % endfor

        ##<!-- DataTables -->
        ##<script type="text/javascript" charset="utf8" src="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.min.js"></script>

        <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
        <!--[if lt IE 9]>
        ##  <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
        <![endif]-->

        <link rel="unapi-server" type="application/xml" title="unAPI" href="${request.route_url('unapi')}">
        <script src="${request.route_url('_js')}"></script>
        <%block name="head"> </%block>
    </head>
    <body id="r-${request.matched_route.name if request.matched_route else 'body'}">
        <div id="header" class="container-fluid">
            <%block name="header"></%block>
        </div>

        <div class="navbar navbar-static-top">
            <div class="navbar-inner">
                <div class="container-fluid">
                    <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </a>
                    ##<a class="brand" href="#">Project name</a>
                    <div class="nav-collapse collapse">
                        ##<p class="navbar-text pull-right">
                        ##  Logged in as <a href="#" class="navbar-link">Username</a>
                        ##</p>
                        <ul class="nav">
                        % for name, item in request.registry.getUtility(IMenuItems).items():
                        <% href, title = item(context.get('ctx'), request) %>
                            <li id="menuitem_${name}" class="${'active' if name == self.attr.active_menu_item else ''}">
                                <a href="${href}" title="${title}">${title}</a>
                            </li>
                        % endfor
                        </ul>
                        % if hasattr(self, 'contextnav'):
                        <br>
                        <ul class="nav pull-right">
                            ${self.contextnav()}
                        </ul>
                        % endif
                    </div><!--/.nav-collapse -->
                </div>
            </div>
        </div>
        <div class="container-fluid">
            % if ctx and getattr(ctx, 'metadata', None):
            <abbr class="unapi-id" title="${h.urlescape(request.resource_url(ctx))}"></abbr>
            % endif
            ##
            ## TODO: loop over sidebar boxes registered for the current page
            ##
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
            <footer>
                <%block name="footer">clld</%block>
            </footer>
        </div>

        <div id="Modal" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="ModalLabel" aria-hidden="true">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h3 id="ModalLabel"></h3>
            </div>
            <div id="ModalBody" class="modal-body">
            </div>
            ##<div class="modal-footer">
            ##    <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
            ##</div>
        </div>

        <script>
$(document).ready(function() {
    $('.ttip').tooltip({placement: 'bottom', delay: {hide: 300}});
});
            <%block name="javascript"> </%block>
        </script>
    </body>
</html>
