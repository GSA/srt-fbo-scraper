import unittest
from unittest.mock import patch
import sys
import os
from scipy import stats
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from utils.train import prepare_samples, train, get_param_distribution, log_uniform
from utils.db.db import Notice, NoticeType, Attachment, Model, now_minus_two
from utils.db.db_utils import get_db_url, session_scope, insert_updated_nightly_file, \
                              DataAccessLayer, clear_data, object_as_dict, fetch_notice_type_id, \
                              insert_model, insert_notice_types, retrain_check, \
                              get_validation_count, get_trained_count, \
                              get_validated_untrained_count, fetch_validated_attachments, \
                              fetch_last_score

class TrainTestCase(unittest.TestCase):
    def setUp(self):
        self.attachments = [
            {
            'text':"this is a test of automagic.",
            'target':1
            },
            {
            'text':"this is a test of automagic.",
            'target':1
            },
            {
            'text':"this is another test.",
            'target':1
            },
            {
            'text':"this is another test. ",
            'target':1
            },
            {
            'text':'this is another test',
            'target':1
            },{
            'text':'this is another test',
            'target':1
            },{
            'text':'this is another test',
            'target':0
            },{
            'text':'this is another test',
            'target':0
            },{
            'text':'this is another test',
            'target':0
            },{
            'text':'this is another test',
            'target':0
            },{
            'text':'this is another test',
            'target':0
            },{
            'text':'this is another test',
            'target':1
            },
            {
            'text':"this is a test of automagic.",
            'target':1
            },
            {
            'text':"this is a test of automagic.",
            'target':1
            },
            {
            'text':"this is a test of automagic.",
            'target':1
            },
            {
            'text':"this is a test of the grid search.",
            'target':0
            },
            {
            'text':"this is a test of the grid search.",
            'target':0
            },{
            'text':"this is a test of the grid search.",
            'target':0
            },{
            'text':"this is a test of the grid search.",
            'target':0
            },{
            'text':"this is a test of the grid search.",
            'target':0
            },{
            'text':"this is a test of the grid search.",
            'target':0
            },{
            'text':"this is a test of the grid search.",
            'target':0
            }
        ]

    def tearDown(self):
        self.attachments = None

    def test_prepare_samples(self):
        X, _ = prepare_samples(self.attachments)
        result = len(X)
        expected = 22
        self.assertEqual(result, expected)

    @patch('utils.train.get_param_distribution')
    def test_train(self, param_dist_mock):
        param_dist = {
                    "vectorizer__ngram_range":[(1,1), (1,2)],
                    "vectorizer__min_df":stats.randint(1,3),
                    "vectorizer__max_df":stats.uniform(.95,.3),
                    "vectorizer__sublinear_tf":[True, False],
                    "select__k":['all'],
                    "clf__alpha": log_uniform(-5,2),
                    "clf__penalty": ['l2','l1','elasticnet'],
                    "clf__loss": ['hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron'],
                    }
        param_dist_mock.return_value = param_dist
        X, y = prepare_samples(self.attachments)
        try:
            _, _, _, _ = train(X, 
                               y,
                               n_iter_search = 10,
                               score = "accuracy")
        except:
            self.fail("train() raised an exception!")
                                                                         

if __name__ == '__main__':
    unittest.main()