# update_assoc_tables.py - adapt unique and nullable

# TODO: DomainElement: reverse UNIQUE(name, parameter_pk)?, parameter_pk NOT NULL?
# TODO: LanguageSource: orm.relationships missing?
# TODO: Unit: language_pk NOT_NULL, innerjoin=True?
# TODO: UnitDomainElement: add UNIQUE(unitparameter_pk, name)?, unitparameter_pk NOT NULL?

import sqlalchemy as sa

UNIQUE_NULL = [
    ('contributioncontributor',
        ['contribution_pk', 'contributor_pk'], []),
    ('contributionreference',
        ['contribution_pk', 'source_pk', 'description'],
        ['description']),
    ('editor',
        ['dataset_pk', 'contributor_pk'], []),
    ('languageidentifier',
        ['language_pk', 'identifier_pk'], []),
    ('languagesource',
        ['language_pk', 'source_pk'], []),
    ('sentencereference',
        ['sentence_pk', 'source_pk', 'description'],
        ['description']),
    ('unitvalue',  # NOTE: <unit, unitparameter, contribution> can have multiple values and also multiple unitdomainelements
        ['unit_pk', 'unitparameter_pk', 'contribution_pk', 'name', 'unitdomainelement_pk'],
        ['contribution_pk', 'name', 'unitdomainelement_pk']),
    ('value',  # NOTE: <language, parameter, contribution> can have multiple values and also multiple domainelements
        ['valueset_pk', 'name', 'domainelement_pk'],
        ['name', 'domainelement_pk']),
    ('valuesentence',
        ['value_pk', 'sentence_pk'], []),
    ('valueset',
        ['language_pk', 'parameter_pk', 'contribution_pk'],
        ['contribution_pk']),
    ('valuesetreference',
        ['valueset_pk', 'source_pk', 'description'],
        ['description']),
]

UNIQUE = [(tab, cols) for tab, cols, nullable in UNIQUE_NULL]

NOTNULL = [(tab, [c for c in cols if c not in nullable]) for tab, cols, nullable in UNIQUE_NULL]


def upgrade():
    conn = op.get_bind()

    def select_null(tab, cols):
        condition = ' OR '.join('%s IS NULL' % c for c in cols)
        return sa.text('SELECT * FROM %(tab)s WHERE %(condition)s' % locals(), conn)

    nulls = [(tab, cols, select_null(tab, cols).execute().fetchall())
        for tab, cols in NOTNULL]
    violating = [(tab, cols) for tab, cols, rows in nulls if rows]
    if violating:
        for tab, cols, rows in violating:
            print('violating %s NOT NULL(%s): %d' % (tab, ', '.join(cols), len(rows)))
        raise RuntimeError

    def select_duplicate(tab, cols):
        cols = ', '.join(cols)
        return sa.text('SELECT %(cols)s, count(*) FROM %(tab)s '
            'GROUP BY %(cols)s HAVING count(*) > 1 ORDER BY %(cols)s' % locals(), conn)

    duplicates = [(tab, cols, select_duplicate(tab, cols).execute().fetchall())
        for tab, cols in UNIQUE]
    violating = [(tab, cols, rows) for tab, cols, rows in duplicates if rows]
    if violating:
        for tab, cols, rows in violating:
            print('violating %s UNIQUE(%s): %d' % (tab, ', '.join(cols), len(rows)))
        raise RuntimeError

    select_nullable = sa.text('SELECT attname FROM pg_attribute '
        'WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = :tab) '
        'AND NOT attnotnull AND attname = ANY(:cols) ORDER BY attnum', conn)

    select_const = sa.text('SELECT name, definition FROM ('
        'SELECT c.conname AS name, pg_get_constraintdef(c.oid) AS definition, '
        'array(SELECT a.attname::text FROM unnest(c.conkey) AS n '
        'JOIN pg_attribute AS a ON a.attrelid = c.conrelid AND a.attnum = n '
        'ORDER BY a.attname) AS names '
        'FROM pg_constraint AS c WHERE c.contype = :type AND c.conrelid = '
        '(SELECT oid FROM pg_class AS t WHERE t.relname = :tab)) AS s '
        'WHERE s.names @> :cols AND s.names <@ :cols',
        conn).bindparams(type='u')

    for tab, cols in NOTNULL:
        for col, in select_nullable.execute(tab=tab, cols=cols).fetchall():
            op.alter_column(tab, col, nullable=False)

    for tab, cols in UNIQUE:
        matching = select_const.execute(tab=tab, cols=cols).fetchall()
        if matching:
            assert len(matching) == 1
            name, definition = matching[0]
            if definition == 'UNIQUE (%s)' % ', '.join(cols):
                continue
            op.drop_constraint(name, tab)
        name = '%s_%s_key' % (tab, '_'.join(cols))
        op.create_unique_constraint(name, tab, cols)

    raise NotImplementedError
