import unittest
import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.mock_opps import mock_schematized_opp_two
from fbo_scraper.db.db import Notice, NoticeType, Solicitation, Attachment, Model, now_minus_two
from fbo_scraper.db.db_utils import get_db_url, session_scope, insert_data_into_solicitations_table, \
    DataAccessLayer, insert_notice_types, update_solicitation_history, search_for_agency, handle_attachments, apply_predictions_to

from datetime import datetime, timedelta


from unittest import mock
from unittest.mock import Mock

from sqlalchemy.orm.session import close_all_sessions
from fbo_scraper.db.db_utils import clear_data

@pytest.mark.usefixtures("db_class")
class DBTestCase(unittest.TestCase):

    def setUp(self):
        self.dal.create_test_postgres_db()
        self.dal.connect()

        with session_scope(self.dal) as session:
            insert_notice_types(session)


    def tearDown(self):
        with session_scope(self.dal) as session:
            clear_data(session)
        close_all_sessions()
        self.dal.drop_test_postgres_db()
        self.dal = None
        self.data = None

    def test_insert_data_into_solicitations_table(self):
        with session_scope(self.dal) as session:
            try:
                insert_data_into_solicitations_table(session, [mock_schematized_opp_two])
            except Exception as e:
                print (e)

def test_update_solicitation_history():
    # Create a mock solicitation object
    class MockSolicitation:
        def __init__(self):
            self.date = None
            self.history = None
            self.updatedAt = None
            self.action = None
            self.actionDate = None
            self.actionStatus = None
            self.predictions = None

    now = datetime.now()

    # Test case 1: new solicitation
    sol1 = MockSolicitation()
    update_solicitation_history(sol1, now, in_database=False)
    assert sol1.action[0]["action"] == "Solicitation Posted"
    assert sol1.actionDate == now
    assert sol1.actionStatus == "Solicitation Posted"
    assert sol1.predictions == { "value": "red", "508": "red", "estar": "red", "history" : [] }

    # Test case 2: existing solicitation with no history
    sol2 = MockSolicitation()
    sol2.date = now
    update_solicitation_history(sol2, now, in_database=True, posted_at=now - timedelta(days=7))
    assert sol2.history[0]["action"] == "Solicitation Updated on SAM"
    assert sol2.updatedAt == now.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Test case 3: existing solicitation with history
    sol3 = MockSolicitation()
    sol3.date = now
    sol3.history = [{ "date": "2022-01-01T00:00:00Z", "user": "admin", "action": "Solicitation Created", "status": "complete" }]
    update_solicitation_history(sol3, now, in_database=True, posted_at=now - timedelta(days=7))
    assert sol3.history[1]["action"] == "Solicitation Updated on SAM"
    assert sol3.updatedAt == now.strftime("%Y-%m-%dT%H:%M:%SZ")

def test_search_for_agency():
    # Create a mock AgencyAlias object
    class MockAgencyAlias:
        def __init__(self, alias, agency_id):
            self.alias = alias
            self.agency_id = agency_id

    # Create a mock Agencies object
    class MockAgencies:
        def __init__(self, id, agency):
            self.id = id
            self.agency = agency
            self.agency_id = id


    # Create a mock Solicitation object
    class MockSolicitation:
        def __init__(self, solNum):
            self.solNum = solNum
            self.agency_id = None
            self.agency = None

    # Create a mock SQLAlchemy session object
    session = Mock()

    # Test case 1: agency alias found
    agency_alias = MockAgencyAlias("ABC", 1)
    agency = MockAgencies(1, "ABC Agency")
    session.query.return_value.filter.return_value.count.return_value = 1
    session.query.return_value.one.return_value = agency_alias
    session.query.return_value.filter.return_value.one.return_value = agency
    sol = MockSolicitation("123")
    search_for_agency("ABC", sol, session)
    assert sol.agency_id == 1
    assert sol.agency == "ABC Agency"

    # Test case 2: agency alias not found
    session.query.return_value.filter.return_value.count.return_value = 0
    sol = MockSolicitation("456")
    search_for_agency("XYZ", sol, session)
    assert sol.agency_id == None
    assert sol.agency == None


def test_handle_attachments():
    # Create a mock Solicitation object
    class MockSolicitation:
        def __init__(self, notice_type_id, parseStatus, na_flag):
            self.notice_type_id = notice_type_id
            self.parseStatus = parseStatus
            self.na_flag = na_flag
            self.attachments = []
            self.numDocs = 0

    # Create a mock opportunity dictionary
    opportunity = {
        "attachments": [
            {
                "filename": "attachment1.txt",
                "machine_readable": True,
                "text": "This is attachment 1.",
                "prediction": 1,
                "decision_boundary": 0.5,
                "validation": True,
                "url": "http://example.com/attachment1.txt",
                "trained": False
            },
            {
                "filename": "attachment2.txt",
                "machine_readable": False,
                "text": "",
                "prediction": 0,
                "decision_boundary": 0.5,
                "validation": False,
                "url": "http://example.com/attachment2.txt",
                "trained": True
            }
        ]
    }

    # Test case 1: attachments present
    now_datetime = datetime.utcnow()
    now_datetime_string = now_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    sol = MockSolicitation(1, [], False)
    handle_attachments(opportunity, sol, now=now_datetime)
    assert sol.numDocs == 2
    assert sol.na_flag == False
    assert len(sol.attachments) == 2
    assert sol.attachments[0].filename == "attachment1.txt"
    assert sol.attachments[0].machine_readable == True
    assert sol.attachments[0].attachment_text == "This is attachment 1."
    assert sol.attachments[0].prediction == 1
    assert sol.attachments[0].decision_boundary == 0.5
    assert sol.attachments[0].validation == True
    assert sol.attachments[0].attachment_url == "http://example.com/attachment1.txt"
    assert sol.attachments[0].trained == False
    assert sol.attachments[1].filename == "attachment2.txt"
    assert sol.attachments[1].machine_readable == False
    assert sol.attachments[1].attachment_text == ""
    assert sol.attachments[1].prediction == 0
    assert sol.attachments[1].decision_boundary == 0.5
    assert sol.attachments[1].validation == False
    assert sol.attachments[1].attachment_url == "http://example.com/attachment2.txt"
    assert sol.attachments[1].trained == True
    assert sol.parseStatus[0]["name"] == "attachment1.txt"
    assert sol.parseStatus[0]["status"] == "successfully parsed"
    assert sol.parseStatus[0]["postedDate"] == now_datetime_string
    assert sol.parseStatus[0]["attachment_url"] == "http://example.com/attachment1.txt"
    assert sol.parseStatus[1]["name"] == "attachment2.txt"
    assert sol.parseStatus[1]["status"] == "processing error"
    assert sol.parseStatus[1]["postedDate"] == now_datetime_string
    assert sol.parseStatus[1]["attachment_url"] == "http://example.com/attachment2.txt"

    # Test case 2: no attachments present
    sol = MockSolicitation(1, [], False)
    opportunity["attachments"] = []
    handle_attachments(opportunity, sol, now=now_datetime)
    assert sol.numDocs == 0
    assert sol.na_flag == True
    assert len(sol.attachments) == 0
    assert len(sol.parseStatus) == 0

    # Test case 3: no machine readable attachemnts
    # Ticket 33: https://trello.com/c/9Voxvpd1
    sol = MockSolicitation(1, [], None)
    opportunity = {
        "attachments": [
            {
                "filename": "attachment2.txt",
                "machine_readable": False,
                "text": "",
                "prediction": 0,
                "decision_boundary": 0.5,
                "validation": False,
                "url": "http://example.com/attachment2.txt",
                "trained": True
            }
        ]
    }
    handle_attachments(opportunity, sol, now=now_datetime)
    assert sol.numDocs == 1
    assert sol.na_flag == True
    assert len(sol.attachments) == 1


@pytest.mark.parametrize("solicitation,prediction, expected", [
    ## Test case 1: Solicitation with grey value and a prediction of 0
    (
    Solicitation(
        na_flag=False,
        predictions={
            'value': 'grey',
            '508': 'grey',
            'estar': 'Not Applicable',
            'history': []
        }
    ), 0, {
        'value': 'red',
        '508': 'red',
        'reviewRec': 'Non-compliant (Action Required)',
        'compliant': 0,
    }),
    ## Test case 2: Solicitation with grey value and a prediction of 1
    (
    Solicitation(
        na_flag=False,
        predictions={
            'value': 'grey',
            '508': 'grey',
            'estar': 'Not Applicable',
            'history': []
        }
    ), 1, 
    {
        'value':'green',
        '508':'green',
        'reviewRec':'Compliant',
        'compliant':1,
    }),
    ## Test case 3: Solicitation with green value, prediciton 1 and na_flag set to True
    (
    Solicitation(
        na_flag=True,
        predictions={
            'value': 'green',
            '508': 'green',
            'estar': 'Compliant',
            'history': []
        }
    ), 1, 
    {
        'value': 'grey',
        '508': 'grey',
        'reviewRec': 'Not Applicable',
        'compliant': None
    }),
    ## Test case 4: Solicitation with green value, prediciton 0 and na_flag set to True
    (
    Solicitation(
        na_flag=True,
        predictions={
            'value': 'green',
            '508': 'green',
            'estar': 'Compliant',
            'history': []
        }
    ), 0, 
    {
        'value': 'grey',
        '508': 'grey',
        'reviewRec': 'Not Applicable',
        'compliant': None
    })
])
def test_apply_predictions_to(solicitation, prediction, expected):
    solicitation.noticeData = {}

    # Call the function with a prediction of 1
    apply_predictions_to(solicitation, prediction)

    # Check that the predictions were updated correctly
    assert solicitation.predictions['value'] == expected['value']
    assert solicitation.predictions['508'] == expected['508']
    assert solicitation.reviewRec == expected['reviewRec']
    assert solicitation.compliant == expected['compliant']    