import unittest
import sys
import os
import logging
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from tests.mock_opps import mock_data_for_db
from utils.db.db import Notice, NoticeType, Attachment, Model, now_minus_two
from utils.db.db_utils import get_db_url, session_scope, insert_data, \
                              DataAccessLayer, clear_data, object_as_dict, fetch_notice_type_id, \
                              insert_model, insert_notice_types, retrain_check, \
                              get_validation_count, get_trained_count, \
                              get_validated_untrained_count, fetch_validated_attachments, \
                              fetch_last_score, fetch_notices_by_solnbr, fetch_notice_type_by_id

from unittest import mock


from unittest import mock


class DBTestCase(unittest.TestCase):
    
    def setUp(self):
        self.data = [mock_data_for_db.copy()]
        self.dal = DataAccessLayer(conn_string = get_db_url())
        self.dal.create_test_postgres_db()
        self.dal.connect()

        with session_scope(self.dal) as session:
            insert_notice_types(session)

        self.maxDiff = None
    
    def tearDown(self):
        with session_scope(self.dal) as session:
            clear_data(session)
        with session_scope(self.dal) as session:
            session.close_all()
        self.dal.drop_test_postgres_db()
        self.dal = None
        self.data = None

    def test_insert_bad_notice(self):

        call_count = 0
        with session_scope(self.dal) as session:
            # intentionally bad notice type
            data = mock_data_for_db.copy()
            data['notice type'] = "not to be found"
            self.assertNotEqual(mock_data_for_db['notice type'], data['notice type'])

            logger = logging.getLogger("utils.db.db_utils")
            print (logger)

            with mock.patch.object(logger, 'warning', wraps=logger.warning):
                insert_data(session, [ data ])
                call_count = logger.warning.call_count
        self.assertEqual (1, call_count, "We should get one warning when adding a notice with a new notice type.")

    def test_insert_notice_types(self):
        with session_scope(self.dal) as session:
            insert_notice_types(session)
        
        types= ['Presolicitation','Solicitation','Combined Synopsis/Solicitation','TRAIN']
        notice_type_ids = []
        for notice_type in types:
            with session_scope(self.dal) as session:
                notice_type_id = session.query(NoticeType.id).filter(NoticeType.notice_type==notice_type).first().id
                notice_type_ids.append(notice_type_id)
        notice_type_ids = set(notice_type_ids)
        result = len(notice_type_ids)
        expected = len(types)
        self.assertEqual(result, expected)
        
    def test_insert_data(self):
        with session_scope(self.dal) as session:
            insert_data(session, self.data)
        result = []
        with session_scope(self.dal) as session:
            notices = session.query(Notice).all()
            for n in notices:
                notice = object_as_dict(n)
                #pop the date and createdAt attributes since they're constructed programmatically
                notice.pop('date')
                notice.pop('createdAt')
                #pop this as it'll vary
                notice.pop('notice_type_id')
                result.append(notice)
        expected = [{'id': 1,
                     'solicitation_number': 'test',
                     'agency': 'agency',
                     'notice_data': {'url': 'url',
                                     'naics': 'test',
                                     'office': 'office',
                                     'subject': 'test',
                                     'classcod': 'test',
                                     'setaside': 'test',
                                     'emails': ['test@test.gov']},
                     'compliant': 0,
                     'feedback': None,
                     'history': None,
                     'action': None,
                     'updatedAt': None,
                     'na_flag': False}]
        self.assertCountEqual(result, expected)

    def test_insert_data_with_new_notice_type(self):
        opp = self.data[0].copy()
        nnt = "new notice type"
        opp['notice type'] = nnt
        with session_scope(self.dal) as session:
            insert_data(session, [opp])
        result = []
        with session_scope(self.dal) as session:
            notices = session.query(Notice).all()
            for n in notices:
                notice = object_as_dict(n)
                notice_type_id = int(notice['notice_type_id'])
                notice_type = fetch_notice_type_by_id(notice_type_id, session)
                self.assertCountEqual(notice_type.notice_type, nnt)


    def test_insert_model(self):
        results = {'c': 'd'}
        params = {'a': 'b'}
        score = .99
        with session_scope(self.dal) as session:
            insert_model(session, 
                         results = results, 
                         params = params, 
                         score = score)
        result = []
        with session_scope(self.dal) as session:
            models = session.query(Model).all()
            for m in models:
                model = object_as_dict(m)
                model.pop('create_date')
                result.append(model)   
        expected = [{'id': 1,
                     'results': results,
                     'params': params,
                     'score': score}]
        self.assertCountEqual(result, expected)

    def test_fetch_last_score(self):
        results = {'c':'d'}
        params = {'a':'b'}
        score = .99
        with session_scope(self.dal) as session:
            insert_model(session, 
                         results = results, 
                         params = params, 
                         score = score)
        with session_scope(self.dal) as session:   
            score = fetch_last_score(session)
        result = score
        expected = .99
        self.assertEqual(result, expected)

    def test_get_validation_count(self):
        with session_scope(self.dal) as session:
            insert_data(session, self.data)
        with session_scope(self.dal) as session:
            result = get_validation_count(session)
        expected = 0
        self.assertEqual(result, expected)

    def test_get_trained_count(self):
        with session_scope(self.dal) as session:
            insert_data(session, self.data)
        with session_scope(self.dal) as session:
            result = get_trained_count(session)
        expected = 0
        self.assertEqual(result, expected)

    def test_get_validated_untrained_count(self):
        with session_scope(self.dal) as session:
            insert_data(session, self.data)
        with session_scope(self.dal) as session:
            result = get_validated_untrained_count(session)
        expected = 0
        self.assertEqual(result, expected)

    def test_retrain_check(self):
        with session_scope(self.dal) as session:
            insert_data(session, self.data)
        with session_scope(self.dal) as session:
            result = retrain_check(session)
        expected = False
        self.assertEqual(result, expected)

    def test_fetch_validated_attachments(self):
        with session_scope(self.dal) as session:
            insert_data(session, self.data)
        with session_scope(self.dal) as session:
            attachments = fetch_validated_attachments(session)
        result = len(attachments)
        # 993 since that's how many docs were initially labeled
        expected = 993
        self.assertEqual(result, expected)

    def test_fetch_notices_by_solnbr(self):
        with session_scope(self.dal) as session:
            insert_data(session, self.data)
        with session_scope(self.dal) as session:
            notices = fetch_notices_by_solnbr('test', session)
        result = len(notices)
        expected = 1
        self.assertEqual(result, expected)

    def test_fetch_notices_by_solnbr_bogus_solnbr(self):
        with session_scope(self.dal) as session:
            insert_data(session, self.data)
        with session_scope(self.dal) as session:
            notices = fetch_notices_by_solnbr('notexist', session)
        result = len(notices)
        expected = 0
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
