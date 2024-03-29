import pytest
import os
import sys
import unittest
from fbo_scraper.db.db_utils import DataAccessLayer
from fbo_scraper.db.connection import get_db_url


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fbo_scraper import sam_utils
from sqlalchemy.orm.session import close_all_sessions
from fbo_scraper.db.db_utils import clear_data

@pytest.mark.usefixtures("db_class")
class SamUtilsTestCase(unittest.TestCase):

    def setUp(self):
        self.dal.create_test_postgres_db()
        self.dal.connect()

    def tearDown(self):
        with self.dal.Session.begin() as session:
            clear_data(session)
        close_all_sessions()
        self.dal.drop_test_postgres_db()
        self.dal = None
        self.data = None

    def test_update_old_solicitations(self):

        with self.dal.Session.begin() as session:
            sam_utils.update_old_solicitations(session, age_cutoff=365, max_tests=5)

if __name__ == '__main__':
    unittest.main()