import unittest
from unittest.mock import patch
import sys
import os
from scipy import stats
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from ..fbo import main
from ..utils.db.db_utils import get_db_url, session_scope, insert_updated_nightly_file, \
                              DataAccessLayer, clear_data

class EndToEndTest(unittest.TestCase):
    def setUp(self):
        conn_string = get_db_url()
        self.dal = DataAccessLayer(conn_string)
        self.dal.create_test_postgres_db()
        self.dal.connect()
        self.main = main

    def tearDown(self):
        with session_scope(self.dal) as session:
            clear_data(session)
        with session_scope(self.dal) as session:
            session.close_all()
        self.dal.drop_test_postgres_db()
        self.dal = None
        self.main = None

    @patch('utils.fbo_nightly_scraper')
    def test_main(self, fbo_mock):
        nfbo = fbo_mock.NightlyFBONotices.return_value
        # use 10/28 since the 28th's file is only 325 kB
        nfbo.ftp_url = 'ftp://ftp.fbo.gov/FBOFeed20181028'
        with self.subTest():
            self.main()
            self.assertTrue(True)
        with self.subTest():
            cwd = os.getcwd()
            attachments_dir = os.path.join(cwd, 'attachments')
            dir_exists = os.path.isdir(attachments_dir)
            self.assertFalse(dir_exists)