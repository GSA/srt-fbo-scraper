import os
import json
import sys
from contextlib import contextmanager
from sqlalchemy import create_engine, func, case
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
import logging
import utils.db.db as db
import dill as pickle

logging.basicConfig(format='[%(levelname)s] %(message)s')

def clear_data(session):
    meta = db.Base.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())

def get_db_url():
    '''
    Return the db connection string depending on the environment
    '''
    if os.getenv('VCAP_APPLICATION'):
        db_string = os.getenv('DATABASE_URL')
    elif os.getenv('TEST_DB_URL'):
        db_string = os.getenv('TEST_DB_URL')
    else:
        db_string = "postgresql+psycopg2://localhost/test"
    conn_string = db_string.replace('\postgresql', 'postgresql+psycopg2')

    return conn_string



class DataAccessLayer:

    def __init__(self, conn_string):
        self.engine = None
        self.conn_string = conn_string

    def connect(self):
        local = self._create_local_postgres()
        if not local:
            self.engine = create_engine(self.conn_string)
        try:
            db.Base.metadata.create_all(self.engine)
        except Exception as e:
            logging.critical(f"Exception occurred creating database metadata with uri:  \
                               {self.conn_string}. Full traceback here:  {e}", exc_info=True)
            sys.exit(1)
        self.Session = sessionmaker(bind = self.engine)

    def _create_local_postgres(self):
        test_conn_string = self.conn_string == "postgresql+psycopg2://localhost/test"
        if test_conn_string:
            self.engine = create_engine(self.conn_string)
            if not database_exists(self.engine.url):
                create_database(self.engine.url)
                return True
        else:
            return

    def drop_local_postgres_db(self):
        test_conn_string = self.conn_string == "postgresql+psycopg2://localhost/test"
        if database_exists(self.engine.url) and test_conn_string:
            drop_database(self.engine.url)

dal = DataAccessLayer(conn_string = get_db_url())

@contextmanager
def session_scope(dal):
    """Provide a transactional scope around a series of operations."""
    session = dal.Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logging.critical(f"Exception occurred during database session, causing a rollback:  \
                           {e}", exc_info=True)
    finally:
        session.close()


def fetch_notice_type_id(notice_type, session):
    '''
    Fetch the notice id for a given notice_number.

    Parameters:
        notice_number (str): a solicitation number from a notice

    Returns:
        None or notice_type_id (int): if notice_type_id, this is the PK for the notice_type
    '''
    try:
        notice_type_id = session.query(db.NoticeType.id).filter(db.NoticeType.notice_type==notice_type).first().id
    except AttributeError:
        return
    return notice_type_id

def insert_notice_types(session):
    '''
    Insert each of the notice types into the notice_type table if it isn't already there.
    '''
    for notice_type in ['MOD','COMBINE','PRESOL','AMDCSS','TRAIN']:
        notice_type_id = fetch_notice_type_id(notice_type, session)
        if not notice_type_id:
            nt = db.NoticeType(notice_type = notice_type)
            session.add(nt)

def fetch_notice_type_by_id(notice_type_id, session):
    '''
    Fetch a Notice Type SQLAlchemy object given a notice_type_id.

    Parameters:
        notice_type_id (int): the PK id for a notice_type

    Returns:
        None or notice_type_obj (SQL Alchemy Object)
    '''
    try:
        notice_type_obj = session.query(db.NoticeType).get(notice_type_id)
    except AttributeError:
        return
    return notice_type_obj

def insert_model(session, results, params, score):
    '''
    Add model to db.

    Parameters:
        results (dict): a dict of scoring metrics and their values
        params (dict): parameter setting that gave the best results on the hold out data.
        score (float): mean cross-validated score of the best_estimator.
    '''
    model = db.Model(results = results,
                     params = params,
                     score = score)
    session.add(model)

def insert_updated_nightly_file(session, updated_nightly_data_with_predictions):

    insert_notice_types(session)
    for notice_type in updated_nightly_data_with_predictions:
        notice_type_id = fetch_notice_type_id(notice_type, session)
        for notice_data in updated_nightly_data_with_predictions[notice_type]:
            attachments = notice_data.pop('attachments')
            agency = notice_data.pop('agency')
            compliant = notice_data.pop('compliant')
            notice_number = notice_data.pop('solnbr')
            notice = db.Notice(notice_type_id = notice_type_id,
                               notice_number = notice_number,
                               agency = agency,
                               notice_data = notice_data,
                               compliant = compliant)
            for doc in attachments:
                attachment =  db.Attachment(prediction = doc['prediction'],
                                            decision_boundary = doc['decision_boundary'],
                                            attachment_url = doc['url'],
                                            attachment_text = doc['text'],
                                            validation = doc['validation'],
                                            trained = doc['trained'])
                notice.attachments.append(attachment)
            session.add(notice)

def get_validation_count(session):
    validation_count = session.query(func.count(db.Attachment.validation))
    validation_count = validation_count.scalar()
    try:
        validation_count = int(validation_count)
    except TypeError:
        return
    return validation_count

def get_trained_count(session):
    trained_count = session.query(func.sum(case([(db.Attachment.trained == True, 1)], else_ = 0)))
    trained_count = trained_count.scalar()
    try:
        trained_count = int(trained_count)
    except TypeError:
        return
    return trained_count

def get_validated_untrained_count(session):
    validated_untrained_count = session.query(func.sum(case([((db.Attachment.trained == False) & (db.Attachment.validation == 1), 1)], else_ = 0)))
    validated_untrained_count = validated_untrained_count.scalar()
    try:
        validated_untrained_count = int(validated_untrained_count)
    except TypeError:
        return
    return validated_untrained_count

def retrain_check(session):
    validated_untrained_count = get_validated_untrained_count(session)
    trained_count = get_trained_count(session)
    try:
        eps = validated_untrained_count / trained_count
    except (ZeroDivisionError, TypeError):
        return False
    threshold = .2
    if eps >= threshold:
        return True
    else:
        return False

def fetch_notice_id(notice_number, session):
    '''
    Fetch the notice id for a given notice_number.

    Parameters:
        notice_number (str): a solicitation number from a notice

    Returns:
        None or notice_id (int): if notice_id, this is the PK for the notice
    '''
    try:
        notice_id = session.query(db.Notice.id).filter(db.Notice.notice_number==notice_number).first().id
    except AttributeError:
        return
    return notice_id

def fetch_notice_by_id(notice_id, session):
    '''
    Fetch a notice given a notice_id.

    Parameters:
        notice_id (int): the PK id for a notice

    Returns:
        None or notice (SQL Alchemy Object)
    '''
    try:
        notice = session.query(db.Notice).get(notice_id)
    except AttributeError:
        return
    return notice


def fetch_validated_attachments(session):
    '''
    Gets all of the validated attachments (including the original training dataset)
    '''
    validated_attachments = session.query(db.Attachment).filter(db.Attachment.validation.isnot(None))
    attachments = []
    for attachment in validated_attachments:
        text = attachment.text
        validation = attachment.validation
        attachments.append({
            'text':text,
            'target':validation
        })
    
    with open('fixtures/train.pkl', 'rb') as f:
        original_labeled_samples = pickle.load(f)
    
    training_data = attachments + original_labeled_samples

    return training_data

def fetch_last_score(session):
    '''
    Gets the score from the most recently trained model.
    '''
    model = session.query(db.Model).order_by(db.Model.id.desc()).first()
    score = model.score

    return score
