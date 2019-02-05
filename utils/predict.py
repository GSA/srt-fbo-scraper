#!/usr/bin/env python3
import os
import dill as pickle
import json
import re
import string
import sys
from nltk.stem.porter import PorterStemmer
import logging

logger = logging.getLogger(__name__)

class Predict():
    '''
    Make 508 accessibility predictions based on fbo notice attachment texts.

    Parameters:
        json_data (dict): The JSON of a nightly fbo file, where each notice
                          has its attachments and their text.
    '''

    def __init__(self, json_data, best_model_path='utils/binaries/estimator.pkl'):
        self.json_data = json_data
        self.best_model_path = best_model_path


    @staticmethod
    def transform_text(doc):
        """
        Returns stemmed lowercased alpha-only substrings from a string that are b/w 3 and 17 chars long.
        It keeps the substring `508`.

        Parameters:
            doc (str): the text of a single FBO document.

        Returns:
            words (str): a string of space-delimited lower-case alpha-only words (except for `508`)
        """

        #manually define stop_words to avoid nltk.download('stopwords')
        stop_words = {'a','about','above','after','again','against','ain','all','am','an','and','any','are','aren',"aren't",
        'as','at','be','because','been','before','being','below','between','both','but','by','can','couldn',"couldn't",'d','did',
        'didn',"didn't",'do','does','doesn',"doesn't",'doing','don',"don't",'down','during','each','few','for','from','further',
        'had','hadn',"hadn't",'has','hasn',"hasn't",'have','haven',"haven't",'having','he','her','here','hers','herself','him',
        'himself','his','how','i','if','in','into','is','isn',"isn't",'it',"it's",'its','itself','just','ll','m','ma','me','mightn',
        "mightn't",'more','most','mustn',"mustn't",'my','myself','needn',"needn't",'no','nor','not','now','o','of','off','on','once',
        'only','or','other','our','ours','ourselves','out','over','own','re','s','same','shan',"shan't",'she',"she's",'should',
        "should've",'shouldn',"shouldn't",'so','some','such','t','than','that',"that'll",'the','their','theirs','them','themselves',
        'then','there','these','they','this','those','through','to','too','until','up','ve','very','was','wasn',"wasn't",'we',
        'were','weren',"weren't",'what','when','where','which','while','who','whom','why','will','with','won',"won't",'wouldn',"wouldn't",
        'y','you',"you'd","you'll","you're","you've",'your','yours','yourself','yourselves'}
        no_nonsense_re = re.compile(r'^[a-zA-Z^508]+$')
        if not isinstance(doc, str):
            logging.warning(f'Found a non-string doc type of {type(doc)}:  {doc}')
            return str(doc).lower()
        doc = doc.lower()
        doc = doc.split()
        words = ''
        for word in doc:
            m = re.match(no_nonsense_re, word)
            if m:
                match = m.group()
                if match in stop_words:
                    continue
                else:
                    match_len = len(match)
                    if match_len <= 17 and match_len >= 3:
                        porter = PorterStemmer()
                        stemmed = porter.stem(match)
                        words += stemmed + ' '
        words = words.strip()

        return words


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
                    notice['compliant'] = 0 #noncompliant until proven otherwise
                    if 'attachments' in notice:
                        attachments = notice['attachments']
                        compliant_counter = 0
                        for attachment in attachments:
                            text = attachment['text']
                            normalized_text = [Predict.transform_text(text)]
                            pred = int(pickled_model.predict(normalized_text)[0])
                            compliant_counter += 1 if pred == 1 else 0
                            dec_func = pickled_model.decision_function(normalized_text)[0]
                            decision_boundary = float(abs(dec_func))
                            attachment['prediction'] = pred
                            attachment['decision_boundary'] = decision_boundary
                        notice['compliant'] = 0 if compliant_counter == 0 else 1

        return json_data
