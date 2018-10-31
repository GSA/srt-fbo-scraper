import os
import dill as pickle
import pandas as pd
import json
import re
import string
import sys


class Predict():
    '''
    Make 508 accessibility predictions based on fbo notice attachment texts.

    Parameters:
        json_data (dict): The JSON of a nightly fbo file, where each notice
                          has its attachments and their text.
    '''
    
    def __init__(self, json_data, best_model_path='utils/binaries/best_clf_scott.pkl'):
        self.json_data = json_data
        self.best_model_path = best_model_path


    @staticmethod
    def transform_text(text):
        '''
        Strip punctuation and some common string formatting.

        Parameters:
            text (str): a string

        Returns:
            stripped_text (str): a string
        '''

        def remove_punctuation(text):
            regex = re.compile('[%s]' % re.escape(string.punctuation))
            s = regex.sub(' ', text)
            
            return s

        def remove_formatting(text):
            output = text.replace('\t', ' ').\
                          replace('\n', ' ').\
                          replace('\r', ' ').\
                          replace('\x0b', ' ').\
                          replace('\x0c', ' ')
            return output

        stripped_punctuation = remove_punctuation(text)
        stripped_text = remove_formatting(stripped_punctuation)
        
        return stripped_text


    def insert_predictions(self):
        '''
        Inserts predictions and decision boundary for each attachment in the nightly JSON

        Returns:
            json_data (dict): a Python dict representing the updated json data
        '''

        with open(self.best_model_path, 'rb') as f:
            pickled_model = pickle.load(f)
        json_data = self.json_data
        for notice_type in json_data:
            notices = json_data[notice_type]
            if not notices:
                continue
            else:
                for notice in notices:
                    notice['noncompliant'] = 1 #noncompliant until proven otherwise
                    if 'attachments' in notice:
                        attachments = notice['attachments']
                        compliant_counter = 0
                        for attachment in attachments:
                            text = attachment['text']
                            normalized_text = [Predict.transform_text(text)]
                            pred = int(pickled_model.predict(normalized_text)[0])
                            compliant_counter += 1 if pred == 0 else 0
                            dec_func = pickled_model.decision_function(normalized_text)[0]
                            decision_boundary = float(abs(dec_func))
                            attachment['prediction'] = pred
                            attachment['decision_boundary'] = decision_boundary
                        notice['noncompliant'] = 0 if compliant_counter > 0 else 1
        
        return json_data

