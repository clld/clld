from clld.db.models import common

from testutils import handle_dt


def test_Contributions(env):
    from clld.web.datatables.contribution import Contributions

    handle_dt(env['request'], Contributions, common.Contribution)
