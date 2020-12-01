<%inherit file="home_comp.mako"/>

<h3>${_('Contact')} ${h.contactmail(req)}</h3>
<div class="well">
    <p>${_('You can contact us via email at')} <a href="mailto:${request.contact_email_address}">${request.contact_email_address}</a>.</p>
    % if request.registry.settings.get('clld.github_repos') and request.registry.settings.get('clld.github_repos_data'):
    <% srepo = request.registry.settings['clld.github_repos'] %>
    <% drepo = request.registry.settings['clld.github_repos_data'] %>
    <p><a href="https://github.com">GitHub</a> users can also create and discuss bug reports using the following <strong>issue trackers</strong>:</p>
        <ul>
            <li><a href="https://github.com/${drepo}/issues">${drepo}/issues</a> for errata regarding the site content</li>
            <li><a href="https://github.com/${srepo}/issues">${srepo}/issues</a> for problems with the site software</li>
        </ul>
    % endif
</div>
