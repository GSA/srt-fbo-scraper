import unittest
import sys
import os
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from utils.predict import Predict
from tests.mock_opps import mock_transformed_opp_one

class PredictTestCase(unittest.TestCase):

    def setUp(self):
        self.predict = Predict(data = [mock_transformed_opp_one])

    def tearDown(self):
        self.predict = None

    def test_transform_text(self):
        test_text = "This is a testy test that's testing transform_text"
        result = self.predict.transform_text(test_text)
        expected = 'testi test test'
        self.assertEqual(result, expected)

    def test_transform_text_none(self):
        test_text = None
        result = self.predict.transform_text(test_text)
        expected = 'none'
        self.assertEqual(result, expected)

    def test_transform_text_number(self):
        test_text = 123
        result = self.predict.transform_text(test_text)
        expected = '123'
        self.assertEqual(result, expected)

    def test_insert_predictions_value_types(self):
        data = self.predict.insert_predictions()
        decision_boundary = data[0]['attachments'][0]['decision_boundary']
        with self.subTest():
            self.assertIsInstance(decision_boundary, float)
        prediction = data[0]['attachments'][0]['prediction']
        with self.subTest():
            self.assertIsInstance(prediction, int)

    def test_insert_predictions_compliant_insert(self):
        data = self.predict.insert_predictions()
        opp = data[0]
        compliant_value = opp['compliant']
        self.assertIsInstance(compliant_value, int)

if __name__ == '__main__':
    unittest.main()