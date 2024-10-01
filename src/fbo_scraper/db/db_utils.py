from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Union, List
import logging
import os
import sys
from copy import deepcopy
from random import random
from enum import Enum

import dill as pickle
from sqlalchemy import func, case, inspect
from sqlalchemy.engine import Engine
from fbo_scraper.db.db import Solicitation

import fbo_scraper.db.db as db
from fbo_scraper.binaries import Path, binary_path
from fbo_scraper.db.connection import DataAccessLayer
import functools

CACHE_SIZE = 256

logger = logging.getLogger(__name__)

class PredictionEnum(Enum):
    compliant = 0
    non_compliant = 1
    not_applicable = 2
    cannot_evaluate = 3

def object_as_dict(obj):
    """
    When using the ORM to retrieve objects, getting row values in a dict is not
    available by default. The SQLAlchemy inspection system must be used.
    """
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def clear_data(session):
    """
    Clears database content without dropping the schema (for testing)
    """
    meta = db.Base.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())




@contextmanager
def session_scope(dal):
    """Provide a transactional scope around a series of operations."""
    session = dal.Session()
    try:
        yield session
        logger.info("Commiting DB session")
        session.commit()
    except Exception as e:
        session.rollback()
        logger.critical(
            f"Exception occurred during database session, causing a rollback:  \
                        {e}",
            exc_info=True,
        )
    finally:
        session.close()


@functools.lru_cache(CACHE_SIZE)
def fetch_notice_type_id(notice_type, session):
    """
    Fetch the notice_type_id for a given notice_type.

    Parameters:
        notice_type (str): a notice type. One of the following:
            'Combined Synopsis/Solicitation'
            'Presolicitation'
            'Solicitation'
            'TRAIN'

    Returns:
        None or notice_type_id (int): if notice_type_id, this is the PK for the notice_type
    """
    try:
        notice_type_id = (
            session.query(db.NoticeType.id)
            .filter(db.NoticeType.notice_type == notice_type)
            .first()
            .id
        )
    except AttributeError:
        logger.debug("Requested notice type {} was not found.".format(notice_type))
        return

    return notice_type_id


@functools.lru_cache(CACHE_SIZE)
def fetch_notice_type_by_id(notice_type_id, session):
    """
    Fetch the notice_type for a given notice_type_id.

    Parameters:
        notice_type_id (int): a notice type_id

    Returns:
        None or notice_type object
    """
    try:
        notice_type = (
            session.query(db.NoticeType)
            .filter(db.NoticeType.id == notice_type_id)
            .first()
        )
    except AttributeError:
        logger.warn("Requested notice type ID {} was not found.".format(notice_type_id))
        return

    return notice_type


def insert_notice_types(
    session,
    sam_notice_types=[
        "Combined Synopsis/Solicitation",
        "Presolicitation",
        "Solicitation",
        "TRAIN",
        "RFQ",
    ],
):
    """
    Insert each of the notice types into the notice_type table if it isn't already there.
    """

    for notice_type in sam_notice_types:
        notice_type_id = fetch_notice_type_id(notice_type, session)
        if not notice_type_id:
            nt = db.NoticeType(notice_type=notice_type)
            session.add(nt)


def insert_model(session, results, params, score):
    """
    Add a Model to the database.

    Parameters:
        results (dict): a dict of scoring metrics and their values
        params (dict): parameter setting that gave the best results on the hold out data.
        score (float): mean cross-validated score of the best_estimator.
    """
    model = db.Model(results=results, params=params, score=score)
    session.add(model)

def update_solicitation_to_inactive(solnbr, session):
    """
    Given a solicitation number, set the active flag to False.
    """
    sol = fetch_solicitations_by_solnbr(solnbr, session, as_dict=False)
    if sol:
        sol.active = False
        session.add(sol)
        return True
    return False

def posted_date_to_datetime(posted_date_string):
    from dateutil.parser import parse, ParserError
    # double check we didn't pass in a datetime already
    if isinstance(posted_date_string, datetime):
        return posted_date_string

    try:
        return parse(posted_date_string)
    except ParserError:
        logger.error("Unable to parse posted date. Returning current utc datetime.")
        return datetime.now(timezone.utc)

def is_opp_update(existing_date, posted_date, sol_existed_in_db):
    if (
        sol_existed_in_db
        and existing_date
        and posted_date
        and existing_date < posted_date_to_datetime(posted_date)
    ):
        return True
    return False

def datetime_to_string_in(obj: Union[dict, list], str_format="%Y-%m-%dT%H:%M:%SZ"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, datetime):
                obj[k] = v.strftime(str_format)
            elif isinstance(v, dict) or isinstance(v, list):
                datetime_to_string_in(v, str_format)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, datetime):
                obj[i] = v.strftime(str_format)
            elif isinstance(v, dict) or isinstance(v, list):
                datetime_to_string_in(v, str_format)
    return obj

def create_new_or_exisiting_sol(sol_number: str, session) -> Solicitation:
    result = fetch_solicitations_by_solnbr(sol_number, session, as_dict=False)
    sol = None 
    if result:
        sol = result
    else:
        sol = Solicitation()
        sol.active = True
        sol.na_flag = False
    
    return sol

def create_new_or_existing_attachment(doc: dict, session) -> db.Attachment:
    attachment_name = doc.get('filename')
    sol_id = doc.get('sol_id')

    result = None 
    if session is not None:
        result = fetch_sol_attachment_by_name(sol_id, attachment_name, session, as_dict=False)

    attachment = None
    if result:
        result.updatedAt = func.now()  # Update the updatedAt field
        attachment = result
    else:
        attachment =  db.Attachment(notice_type_id=doc['notice_type_id'],
                                    filename=attachment_name,
                                    machine_readable=doc['machine_readable'],
                                    attachment_text=doc['text'],
                                    prediction=doc['prediction'],
                                    decision_boundary=doc['decision_boundary'],
                                    validation=doc['validation'],
                                    attachment_url=doc['url'],
                                    trained=doc['trained'])
    return attachment

def sol_attributes_from(opportunity, solicitation: Solicitation):
    """
    Set the attributes of a Solicitation object from an opportunity dict.

    Args:
       - opportunity (dict): oppportunity data from the API
       - solicitation (Solicitation): a Solicitation sqlalchemy database object
    """
    solicitation.noticeData = datetime_to_string_in(opportunity)
    solicitation.noticeType = opportunity.get('notice type')
    solicitation.solNum = opportunity.get('solnbr')
    solicitation.agency = opportunity.get('agency')
    solicitation.date = opportunity.get('postedDate')
    solicitation.compliant = opportunity.get('compliant')
    solicitation.office = opportunity.get('office')
    # TODO: properly set estar category
    estar = "yes" if random() < .5 else "no"
    solicitation.category_list = {"value": "yes", "it": "yes", "estar": estar }
    solicitation.undetermined = False
    solicitation.title = opportunity.get('subject')
    solicitation.url = opportunity.get('url')
    solicitation.contactInfo = opportunity.get('emails')

    

def search_for_agency(agency, solicitation, session):
    agency_alias_query = session.query(db.AgencyAlias).filter(db.AgencyAlias.alias == agency)
    if agency_alias_query.count() > 0:
        agency_alias = agency_alias_query.one()
        solicitation.agency_id = agency_alias.agency_id
        if (agency_alias.agency_id):
            agency = session.query(db.Agencies).filter(db.Agencies.id == agency_alias.agency_id).one()
            solicitation.agency = agency.agency
            logger.debug("{} mapped to {} for solnum {}".format(agency, solicitation.agency, solicitation.solNum))
    else:
        logger.warning("unable to map agency {} for solnum {}".format(agency, solicitation.solNum))

def update_solicitation_history(solicitation, 
                                now: datetime,
                                in_database: bool = False,
                                posted_at: datetime = None,
                                ):
    
    if isinstance(posted_at, str):
        posted_at = posted_date_to_datetime(posted_at)

    original_sol_date = posted_at or now # need this later to see if this is an update or not
    now_datetime_string = now.strftime("%Y-%m-%dT%H:%M:%SZ")


    if in_database:
        if not solicitation.history:
            solicitation.history = []
        if is_opp_update(existing_date=original_sol_date, posted_date=solicitation.date, sol_existed_in_db=in_database):
            solicitation.history.append({ "date": now_datetime_string, "user": "", "action": "Solicitation Updated on SAM", "status": "" })
        solicitation.updatedAt = now_datetime_string
    else:
        if not solicitation.action:
            solicitation.action = []
        solicitation.action.append({"date": now_datetime_string, "user": "", "action": "Solicitation Posted", "status": "complete"})
        solicitation.actionDate = now
        solicitation.actionStatus = "Solicitation Posted"
        solicitation.predictions = { "value": "red", "508": "red", "estar": "red", "history" : [] }

def handle_attachments(opportunity: dict, solicitation: Solicitation, session=None, now: datetime = datetime.now(timezone.utc)) -> int:
    """
    Create Attachment objects from the opportunity data and attach them to the solicitation.

    Args:
        opportunity (dict): Opportunity data from the API
        solicitation (Solicitation): SQL Alchemy Solicitation object
        now (datetime, optional): Current datetime. Defaults to datetime.now(timezone.utc).
    Returns:
        prediction int: Solicitation prediction returned from attachment value
    """
    prediction = 0
    now_datetime_string = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    parseStatus = []
            
    attachments = opportunity.pop('attachments')
    solicitation.numDocs = len(attachments)
    
    sol_attachments = []

    for doc in attachments:
        doc['notice_type_id'] = solicitation.notice_type_id
        doc['sol_id'] = solicitation.id

        attachment = create_new_or_existing_attachment(doc, session)
        
        prediction += doc['prediction'] # this should be a 0/1 boolean and if any 1 then it's enough to make the total result true
        sol_attachments.append(attachment)
        parse_status_text = "successfully parsed" if doc['machine_readable'] else "processing error"
        parseStatus.append({"id": attachment.id, "name": doc['filename'], "status": parse_status_text, "postedDate": now_datetime_string, "attachment_url": doc['url'] })
    
    solicitation.attachments = sol_attachments

    solicitation.parseStatus = parseStatus

    return prediction

def is_machine_readable(attachments: List[db.Attachment]) -> bool:
    """
    Determine if any of the attachments are machine readable.

    Args:
        attachments (list [Attachment]): List of attachment dicts from the API

    Returns:
        bool: True if any attachment is machine readable, False otherwise.
    """
    if not attachments:
        return False

    for attachment in attachments:
        if attachment.machine_readable:
            return True
    return False

def apply_predictions_to(solicitation: Solicitation, predicition: int):
    new_prediction = deepcopy(solicitation.predictions)  # make a copy - if you only chagne the props then SQAlchamy won't know the object changed

    prediction_result = determine_prediction_value(solicitation, predicition)

    if prediction_result == PredictionEnum.not_applicable:
        solicitation.reviewRec = "Not Applicable"
        new_prediction['value'] = "grey"
        new_prediction['508'] = "grey"
    elif prediction_result == PredictionEnum.compliant:
        new_prediction['value'] = "green"
        new_prediction['508'] = "green"
        solicitation.reviewRec = "Compliant"
        solicitation.compliant = 1
    elif prediction_result == PredictionEnum.non_compliant:
        new_prediction['value'] = "red"
        new_prediction['508'] = "red"
        solicitation.reviewRec = "Non-compliant (Action Required)"
        solicitation.compliant = 0
    else:
        new_prediction['value'] = "yellow"
        new_prediction['508'] = "yellow"
        solicitation.reviewRec = "Cannot Evaluate (Review Required)"

    # add a random estar prediction
    # TODO: properly compute estar prediction
    if solicitation.noticeData.get('epa_psc_match', False):
        estar = "red" if random() < .5 else "green"
    else:
        estar = "Not Applicable"
    new_prediction['estar'] = estar

    new_prediction['history'].append( { "date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "value": new_prediction['value'], "508": new_prediction['value'], "estar": estar}  )
    solicitation.predictions = new_prediction

def grab_notice_type_id(notice_type: str, session: DataAccessLayer) -> int:
    """
    Fetch the notice_type_id for a given notice_type \
    or create notice type if it does not exist.
    """

    if notice_type is None:
        logger.error("Notice type is None. Cannot fetch notice type id.")
        return


    notice_type_id = fetch_notice_type_id(notice_type, session)
    if notice_type_id is None:
        logger.warning("Notice type {} not found. Creating new notice type."
                       .format(notice_type))
        insert_notice_types(session, [notice_type])
        notice_type_id = fetch_notice_type_id(notice_type, session)

    return notice_type_id

def determine_prediction_value(solicitation: Solicitation, predicition: int):
    pred = None

    if solicitation.na_flag:
        pred = PredictionEnum.not_applicable
    else:
        if not solicitation.attachments or not is_machine_readable(solicitation.attachments):
            pred = PredictionEnum.cannot_evaluate
        elif predicition != 0:
            pred = PredictionEnum.compliant
        else:
            pred = PredictionEnum.non_compliant
    return pred

def insert_data_into_solicitations_table(session, data) -> list[Solicitation]:
    """
    Insert opportunities data into the database. 

    Parameters:
        data (list): a list of dicts, each representing a single opportunity

    Returns:
        List of Solicitation objects that were inserted, if needed.
    """
    insert_notice_types(session)
    opp_count = 0
    skip_count = 0

    list_of_sols = []
    for opp in data:
        try:
            now_datetime = datetime.now(timezone.utc)
            notice_type = opp['notice type']
            notice_type_id = fetch_notice_type_id(notice_type, session)

            if notice_type_id == None:
                logger.warning("Notice type '{}' found in Notice {} was not in the database".format(notice_type,
                                                                                                    opp.get('solnbr', '')),
                               extra={
                                   'notice type': notice_type,
                                   'soliciation number': opp.get('solnbr', ''),
                                   'agency': opp.get('agency', '')
                               })
                insert_notice_types(session, [notice_type])
                notice_type_id = fetch_notice_type_id(notice_type, session)


            sol = None

            sol = create_new_or_exisiting_sol(opp['solnbr'], session)
            sol_existed_in_db = True if sol.solNum else False
            sol.notice_type_id = notice_type_id


            sol_attributes_from(opp, solicitation=sol)

            search_for_agency(opp['agency'], sol, session)
            update_solicitation_history(sol, 
                                        now_datetime, 
                                        in_database=sol_existed_in_db,
                                        posted_at=opp.get('postedDate', None))


            sol_prediction = handle_attachments(opp, sol, session=session, now=now_datetime)
            
            
            apply_predictions_to(solicitation=sol, predicition=sol_prediction)
            

            # now set the search text column so that we can easily do a full text search in the API
            safe_date = sol.date if sol.date else " "

            safe_action_date = sol.actionDate.strftime("%Y-%m-%dT%H:%M:%SZ") if sol.actionDate else " "

            sol.searchText = " ".join(
                (
                    sol.solNum,
                    notice_type,
                    sol.title,
                    safe_date,
                    sol.reviewRec,
                    sol.actionStatus or "",
                    safe_action_date,
                    sol.agency,
                    sol.office,
                )
            ).lower()

            list_of_sols.append(sol)
            insert_data_into(session, sol, sol_existed_in_db)

            opp_count += 1

        except Exception as e:
            logger.error(
                "Unhandled error. Data for solictation "
                + opp.get("solnbr", "")
                + " may be lost."
            )
            logger.error(f"Exception: {e}", exc_info=True)
            logger.error("Unexpected error: {}".format(str(sys.exc_info()[0])))

    logger.info(
        "Added {} notice records to the database. {} were skipped.".format(
            opp_count, skip_count
        )
    )

    return list_of_sols

def insert_data_into(db_session, from_sol_model, existed_in_db):
    if not existed_in_db:
        logger.info("Inserting {}".format(from_sol_model.solNum))
        db_session.add(from_sol_model)
    else:
        #print("Updating {}".format(sol.solNum))
        logger.info("Updating {}".format(from_sol_model.solNum))

def get_validation_count(session):
    """
    Gets the number of validated attachment predictions
    """    
    validation_count = session.query(func.count(db.Attachment.validation))
    validation_count = validation_count.scalar()
    try:
        validation_count = int(validation_count)
    except TypeError:
        return
    return validation_count


def get_trained_count(session):
    """
    Gets the number of attachments that have been used to train a model
    """

    trained_count = session.query(func.coalesce(func.sum(case((db.Attachment.trained == True, 1), else_ = 0)), 0))
    trained_count = trained_count.scalar()
    try:
        trained_count = int(trained_count)
    except TypeError:
        return
    return trained_count


def get_validated_untrained_count(session):
    """
    Gets the number of attachments whose predictions have been validated but have not been
    used to train a model.
    """
    validated_untrained_count = session.query(func.coalesce(func.sum(case(((db.Attachment.trained == False) & (db.Attachment.validation == 1), 1), else_ = 0)), 0)).scalar()

    try:
        validated_untrained_count = int(validated_untrained_count)
    except TypeError:
        return
    return validated_untrained_count


def retrain_check(session):
    """
    Returns True if the number of validated-untrained attachments divided by the number of
    trained attachments is greater than .2
    """
    validated_untrained_count = get_validated_untrained_count(session)
    trained_count = get_trained_count(session)
    try:
        eps = validated_untrained_count / trained_count
    except (ZeroDivisionError, TypeError):
        return False
    threshold = 0.2
    if eps >= threshold:
        return True
    else:
        return False

def fetch_notices_by_solnbr(solnbr, session):
    """
    Fetch all notices with a given solicitation number (solnbr).

    Parameters:
        solnbr (str): A solicitation number. For example, 'spe7m119t8133'

    Returns:
        notice_dicts (list): a list of dicts, with each dict representing a notice
    """
    notices = session.query(db.Notice).filter(db.Notice.solicitation_number == solnbr)
    notice_dicts = [object_as_dict(notice) for notice in notices]

    return notice_dicts

@functools.lru_cache(CACHE_SIZE)
def fetch_solicitations_by_solnbr(solnbr: str, session, as_dict: bool=True) -> Union[dict, Solicitation]:
    """
    Fetch the solicitation by a given solicitation number (solnbr).

    Parameters:
        - solnbr (str): A solicitation number. For example, 'spe7m119t8133'.
        - session (SQLAlchemy session): A session object that represents a connection to the database.
        - as_dict (bool): A boolean flag that indicates whether the results should be returned as a list of dictionaries (True) or as a SQLAlchemy query object (False). The default value is True.

    Returns:
        A dictionary representing a solicitation. If the as_dict flag is False, a SQLAlchemy Solicitation model object is returned instead.
    """
    
    solicitation = session.query(db.Solicitation).filter(db.Solicitation.solNum == solnbr).first()
    
    if as_dict:
        sol_dict = object_as_dict(solicitation) if solicitation else None
    else:
        sol_dict = solicitation

    return sol_dict

@functools.lru_cache(CACHE_SIZE)
def fetch_sol_attachment_by_name(solicitation_id, attachment_name:str, session, as_dict:bool=False) -> Union[dict, db.Attachment]:
    """
    Fetch an attachment by its filename.

    Parameters:
        solicitation_id (int): the PK id for a solicitation
        attachment_name (str): the filename of the attachment
        session (SQLAlchemy session): a session object that represents a connection to the database
        as_dict (bool): a boolean flag that indicates whether the results should be returned as a list of dictionaries (True) or as a SQLAlchemy query object (False). The default value is True.
    Returns:
        attachment (dict | Model): a SQL Model or dict representing the attachment
    """
    


    attachment = session.query(db.Attachment).filter(db.Attachment.filename == attachment_name, db.Attachment.solicitation_id == solicitation_id).first()

    if as_dict:
        attachment = object_as_dict(attachment) if attachment else None

    return attachment

def fetch_notice_by_id(notice_id, session):
    """
    Fetch a notice given a notice_id.

    Parameters:
        notice_id (int): the PK id for a notice

    Returns:
        None or notice_dict (dict): a dict representing the notice.
    """
    try:
        notice = session.query(db.Notice).get(notice_id)
    except AttributeError:
        return
    notice_dict = object_as_dict(notice) if notice else None

    return notice_dict


def fetch_validated_attachments(session):
    """
    Gets all of the validated attachments (including the original training dataset)
    """
    validated_attachments = session.query(db.Attachment).filter(
        db.Attachment.validation.isnot(None)
    )
    attachments = []
    for attachment in validated_attachments:
        text = attachment.text
        validation = attachment.validation
        attachments.append({"text": text, "target": validation})
    cwd = os.getcwd()
    if "fbo-scraper" in cwd:
        i = cwd.find("fbo-scraper")
        root_path = cwd[: i + len("fbo-scraper")]
    else:
        i = cwd.find("root")
        root_path = cwd
    trained_data_path = os.path.join(root_path, Path(binary_path, "train.pkl"))
    with open(trained_data_path, "rb") as f:
        original_labeled_samples = pickle.load(f)

    training_data = attachments + original_labeled_samples

    return training_data


def fetch_last_score(session):
    """
    Gets the score from the most recently trained model.
    """
    model = session.query(db.Model).order_by(db.Model.id.desc()).first()
    score = model.score

    return score


def fetch_notices_by_solnbr_and_ntype(solnbr, notice_type, session):
    """
    Given a solicitation number and notice type, return all matching notices.

    Parameters:
        solnbr (str): a solicitation number (e.g. fa860418p1022)
        notice_type (str): a notice type, e.g Presolicitation

    Returns:
        matching_notices (list): a list of matching notices, with each row-object
            as a dict within that list.
    """
    notices = fetch_notices_by_solnbr(solnbr, session)
    notice_type_id = fetch_notice_type_id(notice_type, session)
    matching_notices = [
        notice for notice in notices if notice["notice_type_id"] == notice_type_id
    ]

    return matching_notices


def fetch_notice_attachments(notice_id, session):
    """
    Given a notice_id, fetch all of its attachments.

    Parameters:
        notice_id (int): the primary key for a notice

    Returns:
        attachment_dicts (list): a list of attachment row-objects, each of which represented
                                 as a dict
    """
    attachments = session.query(db.Attachment).filter(
        db.Attachment.notice_id == notice_id
    )

    attachment_dicts = [object_as_dict(a) for a in attachments] if attachments else []

    return attachment_dicts


def drop_everything(engine: Engine):
    """(On a live db) drops all foreign key constraints before dropping all tables.
    Workaround for SQLAlchemy not doing DROP ## CASCADE for drop_all()
    (https://github.com/pallets/flask-sqlalchemy/issues/722)
    """
    from sqlalchemy.engine.reflection import Inspector
    from sqlalchemy.schema import (
        DropConstraint,
        DropTable,
        MetaData,
        Table,
        ForeignKeyConstraint,
    )

    con = engine.connect()
    trans = con.begin()
    inspector = Inspector.from_engine(engine)

    # We need to re-create a minimal metadata with only the required things to
    # successfully emit drop constraints and tables commands for postgres (based
    # on the actual schema of the running instance)
    meta = MetaData()
    tables = []
    all_fkeys = []

    for table_name in inspector.get_table_names():
        fkeys = []

        for fkey in inspector.get_foreign_keys(table_name):
            if not fkey["name"]:
                continue

            fkeys.append(ForeignKeyConstraint((), (), name=fkey["name"]))

        tables.append(Table(table_name, meta, *fkeys))
        all_fkeys.extend(fkeys)

    for fkey in all_fkeys:
        con.execute(DropConstraint(fkey))

    for table in tables:
        con.execute(DropTable(table))

    trans.commit()
