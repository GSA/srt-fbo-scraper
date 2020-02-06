from contextlib import contextmanager
import datetime
import json
import logging
import os
import sys

import dill as pickle
from sqlalchemy import create_engine, func, case, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy_utils import database_exists, create_database, drop_database

import utils.db.db as db

logger = logging.getLogger(__name__)

def object_as_dict(obj):
    '''
    When using the ORM to retrieve objects, getting row values in a dict is not 
    available by default. The SQLAlchemy inspection system must be used.
    '''
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

def clear_data(session):
    '''
    Clears database content without dropping the schema (for testing)
    '''
    meta = db.Base.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())

def get_db_url():
    '''
    Return the db connection string depending on the environment
    '''
    if os.getenv('VCAP_SERVICES'):
        db_string = os.getenv('DATABASE_URL')
    elif os.getenv('TEST_DB_URL'):
        db_string = os.getenv('TEST_DB_URL')
    else:
        if not os.getenv('VCAP_APPLICATION'):
            db_string = "postgresql+psycopg2://localhost/test"
        else:
            db_string = None
    if db_string:
        return db_string
    else:
        logger.critical("Exception occurred getting database url")
        sys.exit(1)


class DataAccessLayer:
    '''
    Sets up a connection to the database.
    '''
    test_db_uris = ['postgres://circleci@localhost:5432/smartie-test?sslmode=disable',
                    'postgresql+psycopg2://localhost/test']
    
    def __init__(self, conn_string):
        self.engine = None
        self.conn_string = conn_string

    def connect(self):
        is_test = self.conn_string in DataAccessLayer.test_db_uris
        if is_test:
            if not database_exists(self.conn_string):
                self.create_test_postgres_db()
            #NullPool is a Pool which does not pool connections.
            #Instead it literally opens and closes the underlying DB-API connection 
            # per each connection open/close.
            self.engine = create_engine(self.conn_string, poolclass = NullPool)
        else:
            self.engine = create_engine(self.conn_string)
        try:
            db.Base.metadata.create_all(self.engine)
        except Exception as e:
            logger.critical(f"Exception occurred creating database metadata with uri:  \
                               {self.conn_string}. Full traceback here:  {e}", exc_info=True)
            sys.exit(1)
        self.Session = sessionmaker(bind = self.engine)

    def drop_test_postgres_db(self):
        is_test = self.conn_string in DataAccessLayer.test_db_uris
        if database_exists(self.conn_string ) and is_test:
            drop_database(self.conn_string)

    def create_test_postgres_db(self):
        is_test = self.conn_string in DataAccessLayer.test_db_uris
        if not database_exists(self.conn_string) and is_test:
            create_database(self.conn_string )

@contextmanager
def session_scope(dal):
    """Provide a transactional scope around a series of operations."""
    session = dal.Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.critical(f"Exception occurred during database session, causing a rollback:  \
                        {e}", exc_info=True)
    finally:
        session.close()


def fetch_notice_type_id(notice_type, session):
    '''
    Fetch the notice_type_id for a given notice_type.

    Parameters:
        notice_type (str): a notice type. One of the following:
            'Combined Synopsis/Solicitation'
            'Presolicitation'
            'Solicitation'
            'TRAIN'

    Returns:
        None or notice_type_id (int): if notice_type_id, this is the PK for the notice_type
    '''
    try:
        notice_type_id = session.query(db.NoticeType.id).filter(db.NoticeType.notice_type==notice_type).first().id
    except AttributeError as e:
        logger.error("Requested notice type {} was not found.".format(notice_type))
        return
    
    return notice_type_id

def insert_notice_types(session):
    '''
    Insert each of the notice types into the notice_type table if it isn't already there.
    '''
    sam_notice_types = ['Combined Synopsis/Solicitation', 
                        'Presolicitation', 'Solicitation', 'TRAIN']
    
    for notice_type in sam_notice_types:
        notice_type_id = fetch_notice_type_id(notice_type, session)
        if not notice_type_id:
            nt = db.NoticeType(notice_type = notice_type)
            session.add(nt)


def fetch_notice_type_by_id(notice_type_id, session):
    '''
    Fetch a Notice Type name given a notice_type_id.

    Parameters:
        notice_type_id (int): the PK id for a notice_type

    Returns:
        None or notice_type (str): If not None, the notice type as a str (e.g. 'Solicitation')
    '''
    try:
        notice_type_obj = session.query(db.NoticeType).get(notice_type_id)
        notice_type = notice_type_obj.notice_type
    except AttributeError:
        return
    
    return notice_type

def insert_model(session, results, params, score):
    '''
    Add a Model to the database.

    Parameters:
        results (dict): a dict of scoring metrics and their values
        params (dict): parameter setting that gave the best results on the hold out data.
        score (float): mean cross-validated score of the best_estimator.
    '''
    model = db.Model(results = results,
                     params = params,
                     score = score)
    session.add(model)

def insert_data(session, data):
    '''
    Insert yesterday's SAM data into the database.

    Parameters:
        data (list): a list of dicts, each representing a single opportunity

    Returns:
        None
    '''
    insert_notice_types(session)
    for opp in data:
        notice_type = opp.pop('notice type')
        notice_type_id = fetch_notice_type_id(notice_type, session)

        if notice_type_id == None:
            logger.error("Notice type was not found when inserting record into the notice table.")
            continue

        attachments = opp.pop('attachments')
        agency = opp.pop('agency')
        compliant = opp.pop('compliant')
        solicitation_number = opp.pop('solnbr')
        
        matching_notices = fetch_notices_by_solnbr(solicitation_number, session)
        is_solnbr_in_db = True if matching_notices else False
        
        if is_solnbr_in_db:
            history_date = datetime.datetime.utcnow().strftime("%m/%d/%Y")
            history = [{
                        "date":history_date,
                        "user":"",
                        "action":"Solicitation Updated on SAM",
                        "status":""
                        }]
            notice = db.Notice(notice_type_id = notice_type_id,
                               solicitation_number = solicitation_number,
                               agency = agency,
                               notice_data = opp,
                               compliant = compliant,
                               history = history)
        else:
            notice = db.Notice(notice_type_id = notice_type_id,
                               solicitation_number = solicitation_number,
                               agency = agency,
                               notice_data = opp,
                               compliant = compliant)
        for doc in attachments:
            attachment =  db.Attachment(notice_type_id = notice_type_id,
                                        filename = doc['filename'],
                                        machine_readable = doc['machine_readable'],
                                        attachment_text = doc['text'],
                                        prediction = doc['prediction'],
                                        decision_boundary = doc['decision_boundary'],
                                        validation = doc['validation'],
                                        attachment_url = doc['url'],
                                        trained = doc['trained'])
            notice.attachments.append(attachment)
        session.add(notice)

def get_validation_count(session):
    '''
    Gets the number of validated attachment predictions
    '''
    validation_count = session.query(func.count(db.Attachment.validation))
    validation_count = validation_count.scalar()
    try:
        validation_count = int(validation_count)
    except TypeError:
        return
    return validation_count

def get_trained_count(session):
    '''
    Gets the number of attachments that have been used to train a model
    '''
    trained_count = session.query(func.sum(case([(db.Attachment.trained == True, 1)], else_ = 0)))
    trained_count = trained_count.scalar()
    try:
        trained_count = int(trained_count)
    except TypeError:
        return
    return trained_count

def get_validated_untrained_count(session):
    '''
    Gets the number of attachments whose predictions have been validated but have not been
    used to train a model.
    '''
    validated_untrained_count = session.query(func.sum(case([((db.Attachment.trained == False) & (db.Attachment.validation == 1), 1)], else_ = 0)))
    validated_untrained_count = validated_untrained_count.scalar()
    try:
        validated_untrained_count = int(validated_untrained_count)
    except TypeError:
        return
    return validated_untrained_count

def retrain_check(session):
    '''
    Returns True if the number of validated-untrained attachments divided by the number of 
    trained attachments is greater than .2
    '''
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

def fetch_notices_by_solnbr(solnbr, session):
    '''
    Fetch all notices with a given solicitation number (solnbr).

    Parameters:
        solnbr (str): A solicitation number. For example, 'spe7m119t8133'

    Returns:
        notice_dicts (list): a list of dicts, with each dict representing a notice
    '''
    notices = session.query(db.Notice).filter(db.Notice.solicitation_number == solnbr)
    notice_dicts = [object_as_dict(notice) for notice in notices]
    
    return notice_dicts


def fetch_notice_by_id(notice_id, session):
    '''
    Fetch a notice given a notice_id.

    Parameters:
        notice_id (int): the PK id for a notice

    Returns:
        None or notice_dict (dict): a dict representing the notice.
    '''
    try:
        notice = session.query(db.Notice).get(notice_id)
    except AttributeError:
        return
    notice_dict = object_as_dict(notice)
    
    return notice_dict

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
    cwd = os.getcwd()
    if 'fbo-scraper' in cwd:
        i = cwd.find('fbo-scraper')
        root_path = cwd[:i+len('fbo-scraper')]
    else:
        i = cwd.find('root')
        root_path = cwd
    trained_data_path = os.path.join(root_path, 'utils/binaries/train.pkl')
    with open(trained_data_path, 'rb') as f:
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

def fetch_notices_by_solnbr_and_ntype(solnbr, notice_type, session):
    '''
    Given a solicitation number and notice type, return all matching notices.

    Parameters:
        solnbr (str): a solicitation number (e.g. fa860418p1022)
        notice_type (str): a notice type, e.g Presolicitation

    Returns:
        matching_notices (list): a list of matching notices, with each row-object 
            as a dict within that list.
    '''
    notices = fetch_notices_by_solnbr(solnbr, session)
    notice_type_id = fetch_notice_type_id(notice_type, session)
    matching_notices = [notice for notice in notices if notice['notice_type_id'] == notice_type_id]
    
    return matching_notices

def fetch_notice_attachments(notice_id, session):
    '''
    Given a notice_id, fetch all of its attachments.

    Parameters:
        notice_id (int): the primary key for a notice

    Returns:
        attachment_dicts (list): a list of attachment row-objects, each of which represented 
                                 as a dict
    '''
    attachments = session.query(db.Attachment).filter(db.Attachment.notice_id == notice_id)
    attachment_dicts = [object_as_dict(a) for a in attachments]
    
    return attachment_dicts