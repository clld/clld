
<%def name="contextnav(*items)">
    <ul class="nav nav-pills">
        % for anchor, active in reversed(list(items)):
        <li class="pull-right${' active' if active else ''}">${anchor}</li>
        % endfor
    </ul>
</%def>
