"""
Common data model for clld applications.

We exploit several features of sqlalchemy to make the definition of the data model as
succinct as possible:
- custom declarative base class (see clld.db.meta)
- versioning (see clld.db.versioned)
- joined table inheritance (see clld.db.meta)
- mixins (see clld.db.models.common)

All mapper classes that must be available to attach app-specific custom behaviour are
marked as implementers of the corresponding interface.
"""
