from db import Notice, NoticeType, Model, Version, VersionPrediction, Prediction, Validation, Attachment
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import desc, func,  create_engine
from config import SQLALCHEMY_URI
from datetime import datetime


def create_postgres_db():
    connection_string = SQLALCHEMY_URI
    engine = create_engine(connection_string, echo=False)
    if not database_exists(engine.url):
        create_database(engine.url)
        

def create_notice_type(notice_type, session):
    notice_type = notice_type if len(notice_type) <= 50 else notice_type[:50]
    notice_types = []
    for row in session.query(NoticeType.name).all():
        notice_types.append(row.name)

    if notice_type in notice_types:
        pass
    else:
        notice_type = NoticeType(notice_type = notice_type)
        session.add(notice_type)

