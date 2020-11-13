import os
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import numpy as np
from scipy import stats
from sklearn import metrics
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.linear_model import SGDClassifier, Perceptron
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
#in order to use SMOTE, you've got to import Pipeline from imblearn
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
import dill as pickle
import logging
from utils.predict import Predict

logger = logging.getLogger(__name__)

class log_uniform():
    """
    Provides an instance of the log-uniform distribution with an .rvs() method. Meant to be used with
    RandomizedSearchCV, particularly for params like alpha, C, gamma, etc.

    Attributes:
        a (int or float): the exponent of the beginning of the range
        b (int or float): the exponent of the end of range.
        base (int or float): the base of the logarithm. 10 by default.
    """

    def __init__(self, a=-1, b=0, base=10):
        self.loc = a
        self.scale = b - a
        self.base = base

    def rvs(self, size=1, random_state=None):
        uniform = stats.uniform(loc=self.loc, scale=self.scale)

        return np.power(self.base, uniform.rvs(size=size, random_state=random_state))

def get_param_distribution():
    '''
    Utility function that returns the param distribution for the grid search
    '''
    param_dist = {
                    "vectorizer__ngram_range":[(1,1), (1,2)],
                    "vectorizer__min_df":stats.randint(1,3),
                    "vectorizer__max_df":stats.uniform(.95,.3),
                    "vectorizer__sublinear_tf":[True, False],
                    "select__k":[10,100,200,500,1000,1500,2000,5000],
                    "clf__alpha": log_uniform(-5,2),
                    "clf__penalty": ['l2','l1','elasticnet'],
                    "clf__loss": ['hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron'],
                    }

    return param_dist
    

def train(X, y, weight_classes = True, n_iter_search = 500, score='roc_auc',random_state = 123):
    '''
    Train a binary SGD classifier using a randomized grid search with given scoring metric.

    Parameters:
        X (list-like): list of normalized attachment texts
        y (list-like): list of validated targets (0 = red, 1 = green)
        weight_classes (bool): whether or not to use the “balanced” mode to adjust class weights.
        n_iter_search (int):  number of parameter settings that are sampled. Trades off runtime vs quality
                              of the solution.
        score (str):  the scorer used to evaluate the predictions on the test set. `roc_auc` by
                      default. Available options include:  accuracy, roc_auc, precision, fbeta, recall.
                      Note: for fbeta, beta is set to 1.5 to favor recall of the positive class.
        random_state (int): sets the random seed for reproducibility.
    Returns:
        results (dict): a dict of scoring metrics and their values
        best_score (float): mean cross-validated score of the best_estimator.
        best_estimator (sklearn estimator): estimator that was chosen by the search
        best_params (dict): parameter setting that gave the best results on the hold out data.
    '''

    if weight_classes:
        clf = SGDClassifier(class_weight = 'balanced')
    else:
        clf = clf=SGDClassifier()
    scoring = {'accuracy': metrics.make_scorer(metrics.accuracy_score),
               'roc_auc': metrics.make_scorer(metrics.roc_auc_score),
               'precision': metrics.make_scorer(metrics.average_precision_score),
               'fbeta':metrics.make_scorer(metrics.fbeta_score,beta=.5),
               'recall':metrics.make_scorer(metrics.recall_score)}
    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        y,
                                                        stratify=y,
                                                        test_size=0.2,
                                                        random_state=random_state)
    pipe = Pipeline([('vectorizer', TfidfVectorizer(stop_words='english')),
                        ('select', SelectKBest(chi2)),
                        ('clf', clf)])
    param_dist = get_param_distribution()
    random_search = RandomizedSearchCV(pipe,
                                       param_distributions = param_dist,
                                       scoring = scoring,
                                       refit = score,
                                       n_iter = n_iter_search,
                                       cv = 5,
                                       n_jobs = -1,
                                       verbose = 1,
                                       random_state = random_state)
    try:
        random_search.fit(X_train, y_train)
    except Exception as e:
        logger.error(f"Exception occurred training a new model:  \
                        {e}", exc_info=True)
    y_pred = random_search.predict(X_test)
    #get the col number of the positive class (i.e. green)
    positive_class_col = list(random_search.classes_).index(1)
    try:
        y_score = random_search.predict_proba(X_test)[:,positive_class_col]
    except AttributeError:
        y_score = random_search.decision_function(X_test)
    average_precision = metrics.average_precision_score(y_test, y_score)
    acc = metrics.accuracy_score(y_test,y_pred)
    try:
        roc_auc = metrics.roc_auc_score(y_test, y_pred)
    except ValueError:
        roc_auc = None
    precisions, recalls, _ = metrics.precision_recall_curve(y_test, y_score)
    try:
        auc = metrics.auc(recalls, precisions)
    except ValueError:
        auc = None
    fbeta = metrics.fbeta_score(y_test,y_pred,beta=1.5)
    recall = metrics.recall_score(y_test,y_pred)
    best_estimator = random_search.best_estimator_
    best_params = random_search.best_params_
    best_score = random_search.best_score_
    result_values = [y_pred, y_score, precisions, recall, average_precision,
                     acc, roc_auc, auc, fbeta, recalls, best_score, best_estimator, y_test]
    result_keys = ['y_pred', 'y_score', 'precisions', 'recall', 'average_precision',
                   'acc', 'roc_auc', 'auc', 'fbeta', 'recalls','best_score','best_estimator','y_test']
    results = {k:v for k,v in zip(result_keys,result_values)}

    return results, best_score, best_estimator, best_params

def prepare_samples(attachments):
    '''
    Prepares attachment data for training

    Parameters:
        attachments (list): list of dicts, with each dict containing an attachment's text and
                            validated target
    Returns:
        X (list): list of normalized attachment texts
        y (list): list of validated targets
    '''

    X = []
    y = []
    for attachment in attachments:
        text = Predict.transform_text(attachment['text'])
        X.append(text)
        y.append(attachment['target'])

    return X, y


def pickle_model(best_estimator):
    '''
    Pickles an estimator

    Parameters:
        best_estimator (sklearn estimator): estimator that was chosen by a grid search

    Returns:
        None
    '''

    with open('utils/binaries/atc_estimator.pkl', 'wb') as f:
        pickle.dump(best_estimator, f)