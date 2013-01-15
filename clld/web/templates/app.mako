<!DOCTYPE html>
<html lang="en">
    <% from clld.interfaces import IMenuItems %>
    <%! active_menu_item = "a_home" %>
    <head>
        <meta charset="utf-8">
        <title>   TODO  </title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="">
        <meta name="author" content="">
        <!-- Le styles -->
        <link href="${request.static_url('clld:web/static/css/clld.css')}" rel="stylesheet">
        <link href="${request.static_url('clld:web/static/css/bootstrap.css')}" rel="stylesheet">

        <script type="text/javascript"
                src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCBKZ6iuwHMVqtwkAegSmtCVIboFHk94AA&sensor=false">
        </script>

        <script src="${request.static_url('clld:web/static/js/jquery-1.8.2.js')}"></script>
        <script src="${request.static_url('clld:web/static/js/bootstrap.js')}"></script>
        <script src="${request.static_url('clld:web/static/js/jquery.dataTables.min.js')}"></script>
        <script src="${request.static_url('clld:web/static/openlayers/OpenLayers.js')}"></script>
        <script src="${request.static_url('clld:web/static/js/clld.js')}"></script>

        ##<!-- DataTables CSS -->
        ##<link rel="stylesheet" type="text/css" href="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/css/jquery.dataTables.css">
        ##<!-- jQuery -->
        ##<script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>
        ##<!-- DataTables -->
        ##<script type="text/javascript" charset="utf8" src="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.min.js"></script>

        <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
        <!--[if lt IE 9]>
          <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
        <![endif]-->

        <%block name="head"> </%block>
    </head>
    <body>
        <div class="container-fluid">
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
                        <% href, title = item(context, request) %>
                            <li id="menuitem_${name}" class="${'active' if name == self.attr.active_menu_item else ''}">
                                <a href="${href}" title="${title}">${title}</a>
                            </li>
                        % endfor
                        </ul>
                    </div><!--/.nav-collapse -->
                </div>
            </div>
        </div>

        <%block name="contextnav"></%block>

        <div class="container-fluid">
            ##
            ## TODO: loop over sidebar boxes registered for the current page
            ##

            <div class="row-fluid">
            % if hasattr(self, 'sidebar'):
                <div class="span9">
                ${next.body()}
                </div>
                <div class="span3">
                    ${self.sidebar()}
                </div>
            % else:
                <div class="span12">
                ${next.body()}
                </div>
            % endif
            </div>
            <footer>
                <%block name="footer">clld</%block>
            </footer>
        </div>
        <script>
            <%block name="javascript"> </%block>
        </script>
    </body>
</html>
