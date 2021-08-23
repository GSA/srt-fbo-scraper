import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.mock_opps import mock_schematized_opp_two
from utils.db.db import Notice, NoticeType, Solicitation, Attachment, Model, now_minus_two
from utils.db.db_utils import get_db_url, session_scope, insert_data_into_solicitations_table, \
    DataAccessLayer, clear_data, object_as_dict, fetch_notice_type_id, \
    insert_model, insert_notice_types, retrain_check, \
    get_validation_count, get_trained_count, \
    get_validated_untrained_count, fetch_validated_attachments, \
    fetch_last_score, fetch_notices_by_solnbr, fetch_notice_type_by_id

from unittest import mock

from unittest import mock


class DBTestCase(unittest.TestCase):

    def setUp(self):
        self.dal = DataAccessLayer(conn_string=get_db_url())
        self.dal.connect()

        with session_scope(self.dal) as session:
            insert_notice_types(session)


    def tearDown(self):
        with session_scope(self.dal) as session:
            session.close_all()
        self.dal = None
        self.data = None

    def test_insert_data_into_solicitations_table(self):
        with session_scope(self.dal) as session:
            try:
                insert_data_into_solicitations_table(session, [mock_schematized_opp_two])
            except Exception as e:
                print (e)

