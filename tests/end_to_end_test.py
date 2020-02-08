import os
import sys
import unittest
from unittest.mock import patch


sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from main import main
from utils.db.db_utils import get_db_url, session_scope, DataAccessLayer, clear_data

class EndToEndTest(unittest.TestCase):
    def setUp(self):
        conn_string = get_db_url()
        self.dal = DataAccessLayer(conn_string)
        self.dal.create_test_postgres_db()
        self.dal.connect()

    def tearDown(self):
        with session_scope(self.dal) as session:
            clear_data(session)
        with session_scope(self.dal) as session:
            session.close_all()
        self.dal.drop_test_postgres_db()
        self.dal = None

    def test_main(self):
        with self.subTest():
            main(limit = 20)
            self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()