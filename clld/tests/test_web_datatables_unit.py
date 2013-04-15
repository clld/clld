from clld.tests.util import TestWithEnv
from clld.db.models import common


class Tests(TestWithEnv):
    def test_Units(self):
        from clld.web.datatables.unit import Units

        dt = self.handle_dt(Units, common.Unit)
        self.assertTrue(isinstance(dt.options, dict))

    def test_Values_with_language(self):
        from clld.web.datatables.unit import Units

        lang = common.Language.first()
        self.handle_dt(Units, common.Unit, language=lang)
        self.set_request_properties(params=dict(language=lang.id))
        self.handle_dt(Units, common.Unit)
