import unittest
import sys
import os
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from utils.db.db import Notice, NoticeType, Attachment, Model, now_minus_two
from utils.db.db_utils import get_db_url, session_scope, insert_updated_nightly_file, \
                              DataAccessLayer, clear_data, object_as_dict, fetch_notice_type_id, \
                              insert_model, insert_notice_types, retrain_check, \
                              get_validation_count, get_trained_count, \
                              get_validated_untrained_count, fetch_validated_attachments, \
                              fetch_last_score, fetch_notices_by_solnbr                         

class DBTestCase(unittest.TestCase):
    
    def setUp(self):
        conn_string = get_db_url()
        self.predicted_nightly_data = {'AMDCSS': [{'date': '0506',
                                      'year': '18',
                                      'agency': 'department of justice',
                                      'office': 'federal bureau of investigation',
                                      'location': 'procurement section',
                                      'zip': '20535',
                                      'classcod': '70',
                                      'naics': '511210',
                                      'offadd': '935 pennsylvania avenue, n.w. washington dc 20535',
                                      'subject': 'enterprise business process management software tool',
                                      'solnbr': 'rfp-e-bpm-djf-18-0800-pr-0000828',
                                      'ntype': 'combine',
                                      'contact': 'clark kent, contracting officer, phone 5555555555, email clark.kent@daily-planet.com',
                                      'desc': '  link to document',
                                      'url': 'url',
                                      'setaside': 'n/a',
                                      'popcountry': 'us',
                                      'popzip': '20535',
                                      'popaddress': '935 pennsylvania ave. n.w. washington, dc  ',
                                      'attachments': [{'text': 'test_text_0',
                                                       'url': 'test_url_0',
                                                       'prediction': 1,
                                                       'decision_boundary': 0,
                                                       'validation': None,
                                                       'trained': False},
                                                      {'text': 'test_text_1',
                                                       'url': 'test_url_1',
                                                       'prediction': 1,
                                                       'decision_boundary': 0,
                                                       'validation': None,
                                                       'trained': False},
                                                      {'text': 'test_text_2',
                                                       'url': 'test_url_2',
                                                       'prediction': 1,
                                                       'decision_boundary': 0,
                                                       'validation': None,
                                                       'trained': False},
                                                      {'text': 'test_text_3',
                                                       'url': 'test_url_3',
                                                       'prediction': 1,
                                                       'decision_boundary': 0,
                                                       'validation': None,
                                                       'trained': False},
                                                      {'text': 'test_text_4',
                                                       'url': 'test_url_4',
                                                       'prediction': 1,
                                                       'decision_boundary': 0,
                                                       'validation': None,
                                                       'trained': False},
                                                      {'text': 'test_text_5',
                                                       'url': 'test_url_5',
                                                       'prediction': 1,
                                                       'decision_boundary': 0,
                                                       'validation': None,
                                                       'trained': False},
                                                      {'text': 'test_text_6',
                                                       'url': 'test_url_6',
                                                       'prediction': 1,
                                                       'decision_boundary': 0,
                                                       'validation': None,
                                                       'trained': False}],
                                      'compliant': 0}],
               'MOD': [],
               'COMBINE': [{'date': '0506',
                            'year': '18',
                            'agency': 'defense logistics agency',
                            'office': 'dla acquisition locations',
                            'location': 'dla aviation - bsm',
                            'zip': '23297',
                            'classcod': '66',
                            'naics': '334511',
                            'offadd': '334511',
                            'subject': 'subject',
                            'solnbr': 'spe4a618t934n',
                            'respdate': '051418',
                            'archdate': '06132018',
                            'contact': 'bob.dylan@aol.com',
                            'desc': 'test123',
                            'url': 'test_url',
                            'setaside': 'n/a  ',
                            'attachments': [],
                            'compliant': 0}],
               'PRESOL': []}
        self.predicted_nightly_data_day_two = {'AMDCSS': [{'date': '0506',
                                                           'year': '17',
                                                           'agency': 'defense logistics agency',
                                                           'office': 'dla acquisition locations',
                                                           'location': 'dla aviation - bsm',
                                                           'zip': '23297',
                                                           'classcod': '66',
                                                           'naics': '334511',
                                                           'offadd': '334511',
                                                           'subject': 'subject',
                                                           'solnbr': 'spe4a618t934n',
                                                           'respdate': '051418',
                                                           'archdate': '06132018',
                                                           'contact': 'bob.dylan@aol.com',
                                                           'desc': 'test123',
                                                           'url': 'test_url',
                                                           'setaside': 'n/a  ',
                                                           'attachments': [{'text': 'test_text_0',
                                                                            'url': 'test_url_0',
                                                                            'prediction': 1,
                                                                            'decision_boundary': 0,
                                                                            'validation': None,
                                                                            'trained': False}],
                                                           'compliant': 0}]
                                            }
        self.dal = DataAccessLayer(conn_string = conn_string)
        self.dal.connect()
        self.maxDiff = None
    
    def tearDown(self):
        with session_scope(self.dal) as session:
            clear_data(session)
        self.dal.drop_test_postgres_db()
        self.dal = None
        self.predicted_nightly_data = None
        self.predicted_nightly_data_day_two = None
    
    def test_insert_notice_types(self):
        with session_scope(self.dal) as session:
            insert_notice_types(session)
            notice_types= ['MOD','PRESOL','COMBINE', 'AMDCSS', 'TRAIN']
            notice_type_ids = []
            for notice_type in notice_types:
                notice_type_id = session.query(NoticeType.id).filter(NoticeType.notice_type==notice_type).first().id
                notice_type_ids.append(notice_type_id)
            notice_type_ids = set(notice_type_ids)
        result = len(notice_type_ids)
        expected = len(notice_types)
        self.assertEqual(result, expected)
        
    def test_insert_updated_nightly_file(self):
        with session_scope(self.dal) as session:
            insert_updated_nightly_file(session, self.predicted_nightly_data)
        result = []
        with session_scope(self.dal) as session:
            notices = session.query(Notice).all()
            for n in notices:
                notice = object_as_dict(n)
                #pop the date and createdAt attributes since they're constructed programmatically
                notice.pop('date')
                notice.pop('createdAt')
                result.append(notice)
        expected = [{'id': 1,
                     'notice_type_id': 4,
                     'solicitation_number': 'rfp-e-bpm-djf-18-0800-pr-0000828',
                     'agency': 'department of justice',
                     'notice_data': {'url': 'url',
                                     'zip': '20535',
                                     'date': '0506',
                                     'desc': '  link to document',
                                     'year': '18',
                                     'naics': '511210',
                                     'ntype': 'combine',
                                     'offadd': '935 pennsylvania avenue, n.w. washington dc 20535',
                                     'office': 'federal bureau of investigation',
                                     'popzip': '20535',
                                     'contact': 'clark kent, contracting officer, phone 5555555555, email clark.kent@daily-planet.com',
                                     'subject': 'enterprise business process management software tool',
                                     'classcod': '70',
                                     'location': 'procurement section',
                                     'setaside': 'n/a',
                                     'popaddress': '935 pennsylvania ave. n.w. washington, dc  ',
                                     'popcountry': 'us'},
                     'compliant': 0,
                     'feedback': None,
                     'history': None,
                     'action': None,
                     'updatedAt': None},
                     {'id': 2,
                     'notice_type_id': 2,
                     'solicitation_number': 'spe4a618t934n',
                     'agency': 'defense logistics agency',
                     'notice_data': {'url': 'test_url',
                                     'zip': '23297',
                                     'date': '0506',
                                     'desc': 'test123',
                                     'year': '18',
                                     'naics': '334511',
                                     'offadd': '334511',
                                     'office': 'dla acquisition locations',
                                     'contact': 'bob.dylan@aol.com',
                                     'subject': 'subject',
                                     'archdate': '06132018',
                                     'classcod': '66',
                                     'location': 'dla aviation - bsm',
                                     'respdate': '051418',
                                     'setaside': 'n/a  '},
                     'compliant': 0,
                     'feedback':None,
                     'history':None,
                     'action': None,
                     'updatedAt': None}]
        self.assertCountEqual(result, expected)

    def test_insert_model(self):
        results = {'c':'d'}
        params = {'a':'b'}
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

    def test_insert_updated_nightly_file_day_two(self):
        with session_scope(self.dal) as session:
            insert_updated_nightly_file(session, 
                                        self.predicted_nightly_data)
        with session_scope(self.dal) as session:
            insert_updated_nightly_file(session, 
                                        self.predicted_nightly_data_day_two)
        result = []
        with session_scope(self.dal) as session:
            notices = session.query(Notice).all()
            for n in notices:
                notice = object_as_dict(n)
                #pop the date and createdAt attributes since they're constructed programmatically
                notice.pop('date')
                notice.pop('createdAt')
                result.append(notice)
        expected = [{'id': 1,
                     'notice_type_id': 4,
                     'solicitation_number': 'rfp-e-bpm-djf-18-0800-pr-0000828',
                     'agency': 'department of justice',
                     'notice_data': {'url': 'url',
                                     'zip': '20535',
                                     'date': '0506',
                                     'desc': '  link to document',
                                     'year': '18',
                                     'naics': '511210',
                                     'ntype': 'combine',
                                     'offadd': '935 pennsylvania avenue, n.w. washington dc 20535',
                                     'office': 'federal bureau of investigation',
                                     'popzip': '20535',
                                     'contact': 'clark kent, contracting officer, phone 5555555555, email clark.kent@daily-planet.com',
                                     'subject': 'enterprise business process management software tool',
                                     'classcod': '70',
                                     'location': 'procurement section',
                                     'setaside': 'n/a',
                                     'popaddress': '935 pennsylvania ave. n.w. washington, dc  ',
                                     'popcountry': 'us'},
                     'compliant': 0,
                     'feedback': None,
                     'history': None,
                     'action': None,
                     'updatedAt': None},
                     {'id': 2,
                     'notice_type_id': 2,
                     'solicitation_number': 'spe4a618t934n',
                     'agency': 'defense logistics agency',
                     'notice_data': {'url': 'test_url',
                                     'zip': '23297',
                                     'date': '0506',
                                     'desc': 'test123',
                                     'year': '18',
                                     'naics': '334511',
                                     'offadd': '334511',
                                     'office': 'dla acquisition locations',
                                     'contact': 'bob.dylan@aol.com',
                                     'subject': 'subject',
                                     'archdate': '06132018',
                                     'classcod': '66',
                                     'location': 'dla aviation - bsm',
                                     'respdate': '051418',
                                     'setaside': 'n/a  '},
                     'compliant': 0,
                     'feedback': None,
                     'history': None,
                     'action': None,
                     'updatedAt': None},
                     {'id': 3,
                     'notice_type_id': 4,
                     'solicitation_number': 'spe4a618t934n',
                     'agency': 'defense logistics agency',
                     'notice_data': {'url': 'test_url',
                                     'zip': '23297',
                                     'date': '0506',
                                     'desc': 'test123',
                                     'year': '17',
                                     'naics': '334511',
                                     'offadd': '334511',
                                     'office': 'dla acquisition locations',
                                     'contact': 'bob.dylan@aol.com',
                                     'subject': 'subject',
                                     'archdate': '06132018',
                                     'classcod': '66',
                                     'location': 'dla aviation - bsm',
                                     'respdate': '051418',
                                     'setaside': 'n/a  '},
                     'compliant': 0,
                     'feedback': None,
                     'history': None,
                     'action': None,
                     'updatedAt': None}]
        self.assertCountEqual(result, expected)

    def test_get_validation_count(self):
        with session_scope(self.dal) as session:
            insert_updated_nightly_file(session, self.predicted_nightly_data)
        with session_scope(self.dal) as session:
            result = get_validation_count(session)
        expected = 0
        self.assertEqual(result, expected)

    def test_get_trained_count(self):
        with session_scope(self.dal) as session:
            insert_updated_nightly_file(session, self.predicted_nightly_data)
        with session_scope(self.dal) as session:
            result = get_trained_count(session)
        expected = 0
        self.assertEqual(result, expected)

    def test_get_validated_untrained_count(self):
        with session_scope(self.dal) as session:
            insert_updated_nightly_file(session, self.predicted_nightly_data)
        with session_scope(self.dal) as session:
            result = get_validated_untrained_count(session)
        expected = 0
        self.assertEqual(result, expected)

    def test_retrain_check(self):
        with session_scope(self.dal) as session:
            insert_updated_nightly_file(session, self.predicted_nightly_data)
        with session_scope(self.dal) as session:
            result = retrain_check(session)
        expected = False
        self.assertEqual(result, expected)

    def test_fetch_validated_attachments(self):
        with session_scope(self.dal) as session:
            insert_updated_nightly_file(session, self.predicted_nightly_data)
        with session_scope(self.dal) as session:
            attachments = fetch_validated_attachments(session)
        result = len(attachments)
        expected = 993
        self.assertEqual(result, expected)

    def test_fetch_notices_by_solnbr(self):
        with session_scope(self.dal) as session:
            insert_updated_nightly_file(session, self.predicted_nightly_data)
        with session_scope(self.dal) as session:
            notices = fetch_notices_by_solnbr('rfp-e-bpm-djf-18-0800-pr-0000828', session)
        result = len(notices)
        expected = 1
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()