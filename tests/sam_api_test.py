import unittest
from utils import get_opps
from utils import sam_utils
from utils.db.db_utils import get_db_url, session_scope, DataAccessLayer


class SAMAPITestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_requests_retry_session(self):
        ops = get_opps.get_opps_for_day(limit=100, opportunity_filter_function=sam_utils.opportunity_filter_function)
        self.assertGreater(len(ops), 10)

        for opp in ops:
            if not any(opp['naicsCode'].startswith(n) for n in sam_utils.naics_code_prefixes):
                self.assertTrue(False, f"Failure - opp was returned that had naics code {opp['naicsCode']}. Only naics codes in {','.join(sam_utils.naics_code_prefixes)} should be returned")


    def test_schematize_opps(self):
        opps = get_opps.get_opps_for_day(limit=100, opportunity_filter_function=sam_utils.opportunity_filter_function)
        op = opps[0]
        schematized_opp = get_opps.schematize_opp(op)

        keys = ("noticeId", "title", "solicitationNumber", "agency", "office", "type", "naicsCode", "psc", "classificationCode", "pointOfContact")
        for k in keys:
            self.assertIn(k, schematized_opp)

    def test_transform(self):
        opps = get_opps.get_opps_for_day(limit=10, opportunity_filter_function=sam_utils.opportunity_filter_function)
        get_opps.transform_opps(opps, "/tmp/")

