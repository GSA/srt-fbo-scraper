import os
import sys
import unittest
from utils.db.db_utils import get_db_url, session_scope, DataAccessLayer, insert_data
import pytest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import sam_utils


class SamUtilsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_update_old_solicitations(self):
        conn_string = get_db_url()
        dal = DataAccessLayer(conn_string)
        dal.connect()

        with session_scope(dal) as session:
            sam_utils.update_old_solicitations(session, age_cutoff=365, max_tests=5)

if __name__ == '__main__':
    unittest.main()
