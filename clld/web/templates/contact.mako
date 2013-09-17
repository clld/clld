<%inherit file="home_comp.mako"/>

<h3>Contact ${h.contactmail(req)}</h3>
<div class="well">
    You can contact us via email at <a href="mailto:${request.dataset.contact}">${request.dataset.contact}</a>.
</div>

## TODO: link to github issues for software and data!
