import unittest
import sys
import os
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from utils.predict import Predict
from .fixtures import updated_nightly_data

class PredictTestCase(unittest.TestCase):

    def setUp(self):
        json_data = updated_nightly_data.updated_nightly_data
        self.predict = Predict(json_data = json_data)

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

    def test_insert_predictions_top_level_keys(self):
        json_data = self.predict.insert_predictions()
        result_keys = set(json_data.keys())
        expected_keys = {'COMBINE', 'PRESOL', 'AMDCSS', 'MOD'}
        self.assertEqual(result_keys, expected_keys)

    def test_insert_predictions_bottom_level_keys(self):
        json_data = self.predict.insert_predictions()
        result_keys = set(json_data['PRESOL'][0]['attachments'][0].keys())
        expected_keys = {'trained', 'decision_boundary', 'prediction', 'text', 'validation', 'url'}
        self.assertEqual(result_keys, expected_keys)

    def test_insert_predictions_value_types(self):
        json_data = self.predict.insert_predictions()
        decision_boundary = json_data['PRESOL'][0]['attachments'][0]['decision_boundary']
        with self.subTest():
            self.assertIsInstance(decision_boundary, float)
        prediction = json_data['PRESOL'][0]['attachments'][0]['prediction']
        with self.subTest():
            self.assertIsInstance(prediction, int)

    def test_insert_predictions_compliant_insert(self):
        json_data = self.predict.insert_predictions()
        notice = json_data['PRESOL'][0]
        compliant_value = notice['compliant']
        self.assertIsInstance(compliant_value, int)

if __name__ == '__main__':
    unittest.main()