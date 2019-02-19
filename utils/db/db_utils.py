import os
import json
import sys
from contextlib import contextmanager
from sqlalchemy import create_engine, func, case, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
import logging
import utils.db.db as db
import dill as pickle

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
            logger.critical(f"Exception occurred creating database metadata with uri:  \
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
        logger.critical(f"Exception occurred during database session, causing a rollback:  \
                           {e}", exc_info=True)
    finally:
        session.close()


def fetch_notice_type_id(notice_type, session):
    '''
    Fetch the notice_type_id for a given notice_type.

    Parameters:
        notice_type (str): a notice type. One of ['MOD','COMBINE','PRESOL','AMDCSS','TRAIN']

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
    Fetch a Notice Type name given a notice_type_id.

    Parameters:
        notice_type_id (int): the PK id for a notice_type

    Returns:
        None or notice_type (str): If not None, the notice type as a string (e.g. 'MOD')
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

def insert_updated_nightly_file(session, updated_nightly_data_with_predictions):
    '''
    Insert a night's worth of FBO data into the database.

    Parameters:
        updated_nightly_data_with_predictions (dict): a dict representing a night's worth of FBO data

    Returns:
        None
    '''
    insert_notice_types(session)
    for notice_type in updated_nightly_data_with_predictions:
        notice_type_id = fetch_notice_type_id(notice_type, session)
        for notice_data in updated_nightly_data_with_predictions[notice_type]:
            attachments = notice_data.pop('attachments')
            agency = notice_data.pop('agency')
            compliant = notice_data.pop('compliant')
            solicitation_number = notice_data.pop('solnbr')
            notice = db.Notice(notice_type_id = notice_type_id,
                               solicitation_number = solicitation_number,
                               agency = agency,
                               notice_data = notice_data,
                               compliant = compliant)
            for doc in attachments:
                attachment =  db.Attachment(notice_type_id = notice_type_id,
                                            prediction = doc['prediction'],
                                            decision_boundary = doc['decision_boundary'],
                                            attachment_url = doc['url'],
                                            attachment_text = doc['text'],
                                            validation = doc['validation'],
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

def fetch_notices_by_solnbr_and_ntype(solnbr, notice_type, session):
    '''
    Given a solicitation number and notice type, return all matching notices.

    Parameters:
        solnbr (str): a solicitation number (e.g. fa860418p1022)
        notice_type (str): a notice type, e.g AMDCSS

    Returns:
        matching_notices (list): a list of matching notices, with each row-object as a dict within
                                 that list
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