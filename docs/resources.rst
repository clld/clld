
Resources
=========

Resources are a central concept in CLLD. While we may use the term resource 
also for single instances, more generally a resource is a type of data implementing
an interface to which behaviour can be attached.


Models
------

Each resource is associated with a db model class and optionally with a custom
db model derived from the default one using joined table inheritance.


Adapters
--------

TODO


Routes
------

TODO


Views
-----

clld.web.views 

- index
- detail


Providing custom data for a reources details template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since the view rendering a resources details representations is implemented in
clld core code, clld applications may need a way to provide additional context
for the templates. This can be done by implementing an appropriately named
function in the app.util which will be looked up and called in a BeforeRender
event subscriber.
