import os
import sys
import unittest
import re
from logging import WARNING
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from fbo_scraper.request_utils import requests_retry_session
from fbo_scraper.predict import Predict
from tests.mock_opps import (
    mock_transformed_opp_bad_attachment,
    mock_transformed_opp_one,
)


class RequestUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.params = {
            "cancelled": False,
            "noticeType": "o,p,k,r",
            "size": "100",
            "sortBy": "-modifiedOn",
        }

    def tearDown(self):
        self.params = None

    def test_requests_retry_session(self):
        with requests_retry_session() as session:
            r = session.get("https://www.example.com")
        self.assertTrue(r)

    def test_bad_attachment_detection(self):
        # bad data should get an WARNING log message
        predict = Predict(data = [mock_transformed_opp_bad_attachment])
        with self.assertLogs( level=WARNING) as a:
            predict.insert_predictions()
            msgFound = False
            for msg in a.output:
                if re.match(".*suspicious attachment.*", msg):
                    msgFound = True
            self.assertTrue(msgFound)

        # good data should just have INFO logging
        predict = Predict(data=[mock_transformed_opp_one])
        with self.assertLogs(level=15) as a:
            predict.insert_predictions()
            msgFound = False
            for msg in a.output:
                if re.match(".*suspicious attachment.*", msg):
                    msgFound = True
            self.assertFalse(msgFound)


if __name__ == "__main__":
    unittest.main()
