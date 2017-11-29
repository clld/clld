# update_assoc_tables.py - adapt unique and nullable

# TODO: DomainElement: reverse UNIQUE(name, parameter_pk)?, parameter_pk NOT NULL?
# TODO: LanguageSource: orm.relationships missing?
# TODO: Unit: language_pk NOT_NULL, innerjoin=True?
# TODO: UnitDomainElement: add UNIQUE(unitparameter_pk, name)?, unitparameter_pk NOT NULL?

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = ''
down_revision = ''

# INSTRUCTIONS:
# - cd into the clld app directory
# - $ alembic revision -m "update assoc tables"
# - edit migrations/versions/<...>_update_assoc_tables.py
# - replace the content after 'down_revision = <...>' with the content below
# - $ alembic upgrade head
# - check the output of your "update assoc tables" migration (will end with a RuntimeError)
# - if the changes are as intended, change 'dry=False' to 'dry=True' below
# - run alembic upgrade head once again to apply them

from alembic import op
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


def upgrade(dry=True, verbose=True):
    conn = op.get_bind()

    assert conn.dialect.name == 'postgresql'

    def delete_null_duplicates(tablename, columns, notnull, returning=sa.text('*')):
        assert columns
        table = sa.table(tablename, *map(sa.column, ['pk'] + columns))
        yield table.delete(bind=conn).where(sa.or_(table.c[n] == sa.null() for n in notnull))\
            .returning(returning)
        other = table.alias()
        yield table.delete(bind=conn).where(sa.and_(table.c[n] != sa.null() for n in notnull))\
            .where(sa.exists()
                .where(sa.and_(table.c[c] == other.c[c] for c in columns))
                .where(table.c.pk > other.c.pk))\
            .returning(returning)

    def print_rows(rows, verbose=verbose):
        if not verbose:
            return
        for r in rows:
            print('    %r' % dict(r))

    pgc = sa.table('pg_class', *map(sa.column, ['oid', 'relname']))
    pga = sa.table('pg_attribute', *map(sa.column, ['attrelid', 'attname', 'attnum', 'attnotnull']))

    select_nullable = sa.select([pga.c.attname], bind=conn)\
        .where(pga.c.attrelid == sa.select([pgc.c.oid]).where(pgc.c.relname == sa.bindparam('table')))\
        .where(pga.c.attname == sa.func.any(sa.bindparam('notnull')))\
        .where(~pga.c.attnotnull)\
        .order_by(pga.c.attnum)

    select_const = sa.text('SELECT name, definition FROM ('
        'SELECT c.conname AS name, pg_get_constraintdef(c.oid) AS definition, '
        'array(SELECT a.attname::text FROM unnest(c.conkey) AS n '
        'JOIN pg_attribute AS a ON a.attrelid = c.conrelid AND a.attnum = n '
        'ORDER BY a.attname) AS names '
        'FROM pg_constraint AS c WHERE c.contype = :type AND c.conrelid = '
        '(SELECT oid FROM pg_class AS t WHERE t.relname = :table)) AS s '
        'WHERE s.names @> :cols AND s.names <@ :cols',
        conn).bindparams(type='u')

    for table, unique, null in UNIQUE_NULL:
        print(table)
        notnull = [u for u in unique if u not in null]
        delete_null, delete_duplicates = delete_null_duplicates(table, unique, notnull)

        nulls = delete_null.execute().fetchall()
        if nulls:
            print('%s delete %d row(s) violating NOT NULL(%s)' % (table, len(nulls), ', '.join(notnull)))
            print_rows(nulls)

        duplicates = delete_duplicates.execute().fetchall()
        if duplicates:
            print('%s delete %d row(s) violating UNIQUE(%s)' % (table, len(duplicates), ', '.join(unique)))
            print_rows(duplicates)

        for col, in select_nullable.execute(table=table, notnull=notnull):
            print('%s alter column %s NOT NULL' % (table, col))
            op.alter_column(table, col, nullable=False)

        constraint = 'UNIQUE (%s)' % ', '.join(unique)
        matching = select_const.execute(table=table, cols=unique).fetchall()
        if matching:
            assert len(matching) == 1
            (name, definition), = matching
            if definition == constraint:
                print('%s keep constraint %s %s\n' % (table, name, definition))
                continue
            print('%s drop constraint %s %s' % (table, name, definition))
            op.drop_constraint(name, table)
        name = '%s_%s_key' % (table, '_'.join(unique))
        print('%s create constraint %s %s' % (table, name, constraint))
        op.create_unique_constraint(name, table, unique)
        print('')

    if dry:
        raise RuntimeError('set dry=False to apply these changes')


def downgrade():
    pass
