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
    Make 508 accessibility predictions solicitation document text.

    Parameters:
        data (list): a list of dicts, with each dict representing an opportunity.
    '''

    def __init__(self, data, best_model_path='utils/binaries/estimator.pkl'):
        self.data = data
        cwd = os.getcwd()
        if 'fbo-scraper' in cwd:
            i = cwd.find('fbo-scraper')
            root_path = cwd[:i+len('fbo-scraper')]
        else:
            i = cwd.find('root')
            root_path = cwd
        self.best_model_path = os.path.join(root_path, best_model_path)


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
        data = self.data
        for opp in data:
            opp['compliant'] = 0 #noncompliant until proven otherwise
            if 'attachments' in opp:
                attachments = opp['attachments']
                compliant_counter = 0
                stats = {"chars": [], "prediction": [], "decision boundry": [], "raw prediction": [] }
                for attachment in attachments:
                    text = attachment['text']
                    if re.match('^.?This notice contains link\(s\)',text):
                        logger.warning("Notice {} - {} has suspicious attachment text.".format(opp['solnbr'], opp.get('agency', '') ),
                                     extra={
                                         'text': text[:1024],
                                         'solNum': opp.get('solnbr', ''),
                                         'agency': opp.get('agency', ''),
                                         'notice type': opp.get('notice type', '')
                                     })
                    normalized_text = [Predict.transform_text(text)]
                    raw_prediction = pickled_model.predict(normalized_text)[0]
                    pred = int(raw_prediction)
                    compliant_counter += 1 if pred == 1 else 0
                    dec_func = pickled_model.decision_function(normalized_text)[0]
                    decision_boundary = float(abs(dec_func))
                    attachment['prediction'] = pred
                    attachment['decision_boundary'] = decision_boundary
                    stats['chars'].append(len(attachment['text']))
                    stats['prediction'].append(pred)
                    stats['decision boundry'].append(decision_boundary)
                    stats['raw prediction'].append(int(raw_prediction))
                opp['compliant'] = 0 if compliant_counter == 0 else 1

                logger.log(
                    level= 15,
                    msg="Statistics for notice {} {}".format(opp['agency'],opp['solnbr']),
                    extra={
                        'attachments': len(attachments) ,
                        'chars': sum(stats['chars']),
                        'predictions':stats['prediction'],
                        'decision boundries': stats['decision boundry'],
                        'raw predictions': stats['raw prediction']}
                    )

                if opp['compliant'] == 1:
                    logger.log(level=16, msg="Notice {} {} is predectied to be COMPLIANT".format(opp['agency'], opp['solnbr']) )
                else:
                    logger.log(level=16, msg="Notice {} {} is predectied to be not compliant".format(opp['agency'], opp['solnbr']) )

        return data
