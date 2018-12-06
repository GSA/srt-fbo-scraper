import os
import json
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy import desc, func, case


@contextmanager
def session_scope(dal):
    """Provide a transactional scope around a series of operations."""
    session = dal.Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise #also log
    finally:
        session.close()


def get_db_url():
    '''
    Return the db connection string depending on the environment
    '''
    if os.getenv('VCAP_APPLICATION'):
        db_string = os.getenv('DATABASE_URL')
    elif os.getenv('TEST_DB_URL'):
        db_string = os.getenv('TEST_DB_URL')
    else:
        print("No support for local db testing")
    conn_string = db_string.replace('\postgresql', 'postgresql+psycopg2')
    
    return conn_string


def fetch_notice_type_id(notice_type, session):
    '''
    Fetch the notice id for a given notice_number.

    Parameters:
        notice_number (str): a solicitation number from a notice

    Returns:
        None or notice_type_id (int): if notice_type_id, this is the PK for the notice_type
    '''
    try:
        notice_type_id = session.query(NoticeType.id).filter(NoticeType.notice_type==notice_type).first().id
    except AttributeError:
        return
    return notice_type_id

def add_notice_types(session):
    '''
    Insert each of the notice types into the notice_type table if it isn't already there.
    '''
    for notice_type in ['MOD','COMBINE','PRESOL','AMDCSS','TRAIN']:
        with session_scope(dal) as s:
            notice_type_id = fetch_notice_type_id(notice_type, s)
        if not notice_type_id:
            n = NoticeType(notice_type = notice_type)
            session.add(n)

def fetch_notice_type_by_id(notice_type_id, session):
    '''
    Fetch a Notice Type SQLAlchemy object given a notice_type_id.

    Parameters:
        notice_type_id (int): the PK id for a notice_type

    Returns:
        None or notice_type_obj (SQL Alchemy Object)
    '''
    try:
        notice_type_obj = session.query(NoticeType).get(notice_type_id)
    except AttributeError:
        return
    return notice_type_obj

def add_model_data(estimator, best_params, session):
    '''
    Add model to db.

    Parameters:
        estimator (str): name of the classifier
        best_params (dict): dict of the parameters (best_params_ attribute of classifier instance)
    '''
    model = Model(estimator = estimator,
                  params = best_params)
    session.add(model)
    
def insert_updated_nightly_file(updated_nightly_data_with_predictions):
    with session_scope(dal) as s:
        add_notice_types(s)
    for notice_type in updated_nightly_data_with_predictions:
        with session_scope(dal) as s:
            notice_type_id = fetch_notice_type_id(notice_type, s)
        for notice_data in updated_nightly_data_with_predictions[notice_type]:
            attachments = notice_data.pop('attachments')
            agency = notice_data.pop('agency')
            compliant = notice_data.pop('compliant')
            notice_number = notice_data.pop('solnbr')
            with session_scope(dal) as s:
                notice_type_obj = fetch_notice_type_by_id(notice_type_id, s)
            notice = Notice(notice_number = notice_number,
                            agency = agency,
                            notice_data = 'test',
                            compliant = compliant)
            for doc in attachments:
                attachment =  Attachment(prediction = doc['prediction'],
                                         decision_boundary = doc['decision_boundary'],
                                         attachment_url = doc['url'],
                                         attachment_text = doc['text'],
                                         validation = doc['validation'],
                                         trained = doc['trained'])
                notice.attachments.append(attachment)
            notice.notice_types.append(notice_type_obj)
            with session_scope(dal) as s:
                s.add(notice)                   

def get_validation_count():
    with session_scope(dal) as session:
        count = session.query(func.count(Attachment.validation))
    total = count.scalar()
    return int(total)

def get_trained_amount():
    with session_scope(dal) as session:
        sum_of_trained = session.query(func.sum(case([(Attachment.trained == True, 1)], else_=0)))
    total = sum_of_trained.scalar()
    return int(total) 
    
def revalidation_check():
    with session_scope(dal) as session:
        count_of_total_validated = get_validation_count()
    with session_scope(dal) as session:
        sum_of_trained = get_trained_amount()
    if (count_of_total_validated - sum_of_trained) > 1000:
        return 1
    else:
        return 0

def query_notice(notice, session):
    #TODO: need to build out
    notice_ID = session.query(NoticeType.notice_type).filter(NoticeType.notice_type==notice).first()
    return notice_ID

def get_complaint_amount(session):
    sum_of_compliant = session.query(func.sum(Notice.compliant))
    total = sum_of_compliant.scalar()
    return int(total) 
    
def query_model(estimator, session):
    model = session.query(Model.estimator).filter(Model.estimator==estimator).first()
    return model

def fetch_notice_id(notice_number, session):
    '''
    Fetch the notice id for a given notice_number.

    Parameters:
        notice_number (str): a solicitation number from a notice

    Returns:
        None or notice_id (int): if notice_id, this is the PK for the notice
    '''
    try:
        notice_id = session.query(Notice.id).filter(Notice.notice_number==notice_number).first().id
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
        notice = session.query(Notice).get(notice_id)
    except AttributeError:
        return
    return notice
    

def test_relationships(notice, session):
    notice_id = session.query(Notice.id).filter(Notice.id==Attachment.notice_id, 
                                                NoticeType.notice_type==notice).first()
    return notice_id







