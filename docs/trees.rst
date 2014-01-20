
Handling Trees
--------------

In this chapter we describe how
`tree-structured data <http://en.wikipedia.org/wiki/Tree_%28data_structure%29>`_ my be
modelled in a CLLD app. We use a technique called
`closure table <http://dirtsimple.org/2010/11/simplest-way-to-do-tree-based-queries.html>`_
to make efficient queries of the form "all descendants of x up to depth y" possible.

As an example we describe how the classification of languoids in
`Glottolog <http://glottolog.org>`_ is modelled.

In the data model we extend the core Language model to include a self-referencing foreign
key pointing to the parent in the classification (or Null if the languoid is a top-level
family or isolate).

.. code-block:: python

    @implementer(ILanguage)
    class Languoid(Language, CustomModelMixin):
        pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
        father_pk = Column(Integer, ForeignKey('languoid.pk'))

Then we add the closure table.

.. code-block:: python

    class ClosureTable(Base):
        __tablename__ = 'closuretable'
        parent_pk = Column(Integer, ForeignKey('languoid.pk'))
        child_pk = Column(Integer, ForeignKey('languoid.pk'))
        depth = Column(Integer)

Since data in CLLD apps typically does not change often, and if it does, then in a well-defined,
hopefully scripted, way, we don't create triggers to synchronize closure table updates with
updates of the parent-child relations in the main table, because triggers are typically much
more prone to not being portable across databases.

Instead we include the code to update the closure table in the function
``myapp.scripts.initializedb.prime_cache`` whose explicit aim is to help create de-normalized
data.

.. code-block:: python

    DBSession.execute('delete from closuretable')
    SQL = ClosureTable.__table__.insert()
    ltable = Languoid.__table__

    # store a mapping of pk to father_pk for all languoids:
    father_map = {r[0]: r[1] for r in DBSession.execute('select pk, father_pk from languoid')}

    # we compute the ancestry for each single languoid
    for pk, father_pk in father_map.items():
        depth = 1

        # now follow up the line of ancestors
        while father_pk:
            DBSession.execute(SQL, dict(child_pk=pk, parent_pk=father_pk, depth=depth))
            depth += 1
            father_pk = father_map[father_pk]

With this setup, we can add a method to Languoid to retrieve all ancestors:

.. code-block:: python

    def get_ancestors(self):
        # retrieve the pks of the ancestors ordered by distance, i.e. from direct parent
        # to top-level family:
        pks = [
            r[0] for r in DBSession.query(ClosureTable.parent_pk)
            .filter(ClosureTable.child_pk == self.pk)
            .order_by(ClosureTable.depth)]
        # store the ancestor objects keyed py pk
        ancestors = {
            l.pk: l for l in DBSession.query(Languoid).filter(Languoid.pk.in_(pks))}
        # yield the ancestors in order
        for pk in pks:
            yield ancestors[pk]

.. note::

    We can not simply use the query retrieving the pks from the closure table as subquery
    when retrieving actual Languoid objects, because order of an inner query will be for
    the outer query, thus we would end up with a set of ancestors with no defined order.
