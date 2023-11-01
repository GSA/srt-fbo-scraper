from datetime import datetime
import unittest
import pytest
import sys
import os
import logging
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from tests.mock_opps import mock_schematized_opp_one
from fbo_scraper.db.db import Notice, NoticeType, Attachment, Model, now_minus_two, Solicitation
from fbo_scraper.db.db_utils import (session_scope, insert_data_into_solicitations_table,
                              DataAccessLayer, clear_data, object_as_dict, fetch_notice_type_id,
                              insert_model, insert_notice_types, retrain_check,
                              get_validation_count, get_trained_count,
                              get_validated_untrained_count, fetch_validated_attachments,
                              fetch_last_score, fetch_notices_by_solnbr, fetch_notice_type_by_id, datetime_to_string_in, fetch_solicitations_by_solnbr)

from fbo_scraper.db.connection import get_db_url


from sqlalchemy.orm.session import close_all_sessions


from unittest import mock



@pytest.mark.parametrize("input,expected", [
    (
    ## input
    {
        "date": datetime(2022, 1, 1),
        "nested_dict": {
            "date": datetime(2022, 1, 2)
        },
        "list": [
            datetime(2022, 1, 3),
            {
                "date": datetime(2022, 1, 4)
            }
        ]
    },
    ## expected
    {
        "date": "2022-01-01T00:00:00Z",
        "nested_dict": {
            "date": "2022-01-02T00:00:00Z"
        },
        "list": [
            "2022-01-03T00:00:00Z",
            {
                "date": "2022-01-04T00:00:00Z"
            }
        ]
    }
    )
])
def test_datetime_to_string_in(input, expected):
    result = datetime_to_string_in(input)
    assert result == expected



@pytest.mark.usefixtures("db_class")
class DBTestCase(unittest.TestCase):
    def setUp(self):
        self.data = [mock_schematized_opp_one.copy()]
        self.dal.create_test_postgres_db()
        self.dal.connect()

        with session_scope(self.dal) as session:
            insert_notice_types(session)

        self.maxDiff = None

    def tearDown(self):
        with session_scope(self.dal) as session:
            clear_data(session)
        close_all_sessions()
        self.dal.drop_test_postgres_db()
        self.dal = None
        self.data = None

    def test_insert_bad_notice(self):
        call_count = 0
        with session_scope(self.dal) as session:
            # intentionally bad notice type
            data = mock_schematized_opp_one.copy()
            data['notice type'] = "not to be found"
            self.assertNotEqual(mock_schematized_opp_one['notice type'], data['notice type'])

            logger = logging.getLogger("fbo_scraper.db.db_utils")
            print(logger)

            with mock.patch.object(logger, 'warning', wraps=logger.warning):
                insert_data_into_solicitations_table(session, [ data ])
                call_count = logger.warning.call_count
            assert call_count >= 1, "We should get one warning when adding a notice with a new notice type."

    def test_insert_notice_types(self):
        with session_scope(self.dal) as session:
            insert_notice_types(session)

        types = [
            "Presolicitation",
            "Solicitation",
            "Combined Synopsis/Solicitation",
            "TRAIN",
        ]
        notice_type_ids = []
        for notice_type in types:
            with session_scope(self.dal) as session:
                notice_type_id = (
                    session.query(NoticeType.id)
                    .filter(NoticeType.notice_type == notice_type)
                    .first()
                    .id
                )
                notice_type_ids.append(notice_type_id)
        notice_type_ids = set(notice_type_ids)
        result = len(notice_type_ids)
        expected = len(types)
        self.assertEqual(result, expected)
        
    def test_insert_data_into_solicitations_table(self):
        with session_scope(self.dal) as session:
            insert_data_into_solicitations_table(session, self.data)
        result = []
        with session_scope(self.dal) as session:
            solicitations = session.query(Solicitation).filter(Solicitation.solNum == self.data[0]['solnbr'])
            for s in solicitations:
                notice = object_as_dict(s)
                #pop the date and createdAt attributes since they're constructed programmatically
                notice.pop('date')
                notice.pop('createdAt')
                #pop this as it'll vary
                notice.pop('notice_type_id')
                result.append(notice)
        expected = [{'id': 1,
                     'solNum': 'test',
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
        assert len(result) > 0, "We should have at least one result."
        assert result[0]['solNum'] == expected[0]['solNum'], "The solNum should match."
        assert result[0]['agency'] == expected[0]['agency'], "The agency should match."
        # Test verifying update for Ticket 67: https://trello.com/c/wAhW6CgG
        assert result[0]['reviewRec'] == 'Cannot Evaluate (Review Required)'


    def test_insert_data_into_solicitations_table_with_new_notice_type(self):
        opp = self.data[0].copy()
        nnt = "new notice type"
        opp["notice type"] = nnt
        with session_scope(self.dal) as session:
            insert_data_into_solicitations_table(session, [opp])
        result = []
        with session_scope(self.dal) as session:
            notices = session.query(Notice).all()
            for n in notices:
                notice = object_as_dict(n)
                notice_type_id = int(notice["notice_type_id"])
                notice_type = fetch_notice_type_by_id(notice_type_id, session)
                self.assertCountEqual(notice_type.notice_type, nnt)

    def test_insert_model(self):
        results = {"c": "d"}
        params = {"a": "b"}
        score = 0.99
        with session_scope(self.dal) as session:
            insert_model(session, results=results, params=params, score=score)
        result = []
        with session_scope(self.dal) as session:
            models = session.query(Model).all()
            for m in models:
                model = object_as_dict(m)
                model.pop('create_date')
                id = model.get('id')
                result.append(model)   
        expected = [{ 'id': id,
                    'results': results,
                     'params': params,
                     'score': score}]
        self.assertCountEqual(result, expected)

    def test_fetch_last_score(self):
        results = {"c": "d"}
        params = {"a": "b"}
        score = 0.99
        with session_scope(self.dal) as session:
            insert_model(session, results=results, params=params, score=score)
        with session_scope(self.dal) as session:
            score = fetch_last_score(session)
        result = score
        expected = 0.99
        self.assertEqual(result, expected)

    def test_get_validation_count(self):
        with session_scope(self.dal) as session:
            insert_data_into_solicitations_table(session, self.data)
        with session_scope(self.dal) as session:
            result = get_validation_count(session)
        expected = 0
        self.assertEqual(result, expected)

    def test_get_trained_count(self):
        with session_scope(self.dal) as session:
            insert_data_into_solicitations_table(session, self.data)
        with session_scope(self.dal) as session:
            result = get_trained_count(session)
        expected = 0
        self.assertEqual(result, expected)

    def test_get_validated_untrained_count(self):
        result = None
        with session_scope(self.dal) as session:
            insert_data_into_solicitations_table(session, self.data)
        with session_scope(self.dal) as session:
            result = get_validated_untrained_count(session)
        expected = 0
        self.assertEqual(result, expected)

    def test_retrain_check(self):
        result = None
        with session_scope(self.dal) as session:
            insert_data_into_solicitations_table(session, self.data)
        with session_scope(self.dal) as session:
            result = retrain_check(session)
        expected = False
        self.assertEqual(result, expected)

    def test_fetch_validated_attachments(self):
        attachments = None
        with session_scope(self.dal) as session:
            insert_data_into_solicitations_table(session, self.data)
        with session_scope(self.dal) as session:
            attachments = fetch_validated_attachments(session)
        result = len(attachments)
        # 993 since that's how many docs were initially labeled
        expected = 993
        self.assertEqual(result, expected)

    def test_fetch_solicitations_by_solnbr(self):
        notices = None
        with session_scope(self.dal) as session:
            insert_data_into_solicitations_table(session, self.data)
        with session_scope(self.dal) as session:
            notices = fetch_solicitations_by_solnbr('test', session)
        result = len(notices)
        expected = 28 # Amount of keys in dict
        self.assertEqual(result, expected)

    def test_fetch_solicitations_by_solnbr_bogus_solnbr(self):
        notices = []
        with session_scope(self.dal) as session:
            insert_data_into_solicitations_table(session, self.data)
        with session_scope(self.dal) as session:
            notices = fetch_solicitations_by_solnbr("notexist", session)
        result = len(notices)
        expected = 0
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
