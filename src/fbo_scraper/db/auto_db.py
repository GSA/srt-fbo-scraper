# coding: utf-8
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Table, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.sql import func

Base = declarative_base()
metadata = Base.metadata


class Agency(Base):
    __tablename__ = 'Agencies'

    id = Column(Integer, primary_key=True, server_default=text("nextval('\"Agencies_id_seq\"'::regclass)"))
    agency = Column(String)
    acronym = Column(String)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())


class Prediction(Base):
    __tablename__ = 'Predictions'

    id = Column(Integer, primary_key=True, server_default=text("nextval('\"Predictions_id_seq\"'::regclass)"))
    title = Column(String, nullable=False)
    url = Column(String)
    agency = Column(String)
    numDocs = Column(Integer)
    solNum = Column(String, nullable=False, unique=True)
    noticeType = Column(String, nullable=False)
    date = Column(DateTime)
    office = Column(String)
    na_flag = Column(Boolean)
    eitLikelihood = Column(JSONB(astext_type=Text()))
    undetermined = Column(Boolean)
    action = Column(JSONB(astext_type=Text()))
    actionStatus = Column(String)
    actionDate = Column(DateTime)
    history = Column(JSONB(astext_type=Text()))
    contactInfo = Column(JSONB(astext_type=Text()))
    parseStatus = Column(JSONB(astext_type=Text()))
    predictions = Column(JSONB(astext_type=Text()))
    reviewRec = Column(String)
    searchText = Column(String)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    active = Column(Boolean, server_default=text("true"))


class SequelizeMeta(Base):
    __tablename__ = 'SequelizeMeta'

    name = Column(String(255), primary_key=True)


class Survey(Base):
    __tablename__ = 'Surveys'

    id = Column(Integer, primary_key=True, server_default=text("nextval('\"Surveys_id_seq\"'::regclass)"))
    question = Column(Text)
    choices = Column(JSONB(astext_type=Text()))
    section = Column(String(2000))
    type = Column(String(2000))
    answer = Column(Text)
    note = Column(Text)
    choicesNote = Column(JSONB(astext_type=Text()))
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())


class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, server_default=text("nextval('\"Users_id_seq\"'::regclass)"))
    firstName = Column(String)
    lastName = Column(String)
    agency = Column(String)
    email = Column(String)
    password = Column(String)
    position = Column(String)
    isAccepted = Column(Boolean)
    isRejected = Column(Boolean)
    userRole = Column(String)
    rejectionNote = Column(String)
    creationDate = Column(String)
    tempPassword = Column(String)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    maxId = Column(String(256))


class AgencyAlias(Base):
    __tablename__ = 'agency_alias'

    id = Column(Integer, primary_key=True, server_default=text("nextval('agency_alias_id_seq'::regclass)"))
    agency_id = Column(Integer, nullable=False)
    alias = Column(String)
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)


class Model(Base):
    __tablename__ = 'model'

    id = Column(Integer, primary_key=True, server_default=text("nextval('model_id_seq'::regclass)"))
    results = Column(JSONB(astext_type=Text()))
    params = Column(JSONB(astext_type=Text()))
    score = Column(Float(53))
    create_date = Column(DateTime, nullable=False)


class NoticeType(Base):
    __tablename__ = 'notice_type'

    id = Column(Integer, primary_key=True, server_default=text("nextval('notice_type_id_seq'::regclass)"))
    notice_type = Column(String(50), index=True)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())


class Solicitation(Base):
    __tablename__ = 'solicitations'

    id = Column(Integer, primary_key=True, server_default=text("nextval('solicitations_id_seq'::regclass)"))
    solNum = Column(String, unique=True)
    active = Column(Boolean, server_default=text("true"))
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    title = Column(String)
    url = Column(String)
    agency = Column(String)
    numDocs = Column(Integer)
    notice_type_id = Column(Integer)
    noticeType = Column(String)
    date = Column(DateTime)
    office = Column(String)
    na_flag = Column(Boolean, server_default=text("false"))
    category_list = Column(JSONB(astext_type=Text()))
    undetermined = Column(Boolean)
    history = Column(JSONB(astext_type=Text()), server_default=text("'[]'::jsonb"))
    action = Column(JSONB(astext_type=Text()), server_default=text("'[]'::jsonb"))
    actionDate = Column(DateTime)
    actionStatus = Column(String)
    contactInfo = Column(JSONB(astext_type=Text()))
    parseStatus = Column(JSONB(astext_type=Text()))
    predictions = Column(JSONB(astext_type=Text()), server_default=text("'{\"value\": \"red\", \"history\": []}'::jsonb"))
    reviewRec = Column(String)
    searchText = Column(String)
    compliant = Column(Integer, server_default=text("0"))
    noticeData = Column(JSONB(astext_type=Text()))
    agency_id = Column(Integer)


t_survey_backup = Table(
    'survey_backup', metadata,
    Column('id', Integer),
    Column('question', Text),
    Column('choices', JSONB(astext_type=Text())),
    Column('section', String(2000)),
    Column('type', String(2000)),
    Column('answer', Text),
    Column('note', Text),
    Column('choicesNote', JSONB(astext_type=Text())),
    Column('createdAt', DateTime),
    Column('updatedAt', DateTime)
)


class SurveyResponse(Base):
    __tablename__ = 'survey_responses'

    id = Column(Integer, primary_key=True, server_default=text("nextval('survey_responses_id_seq'::regclass)"))
    solNum = Column(String, index=True)
    contemporary_notice_id = Column(Integer)
    response = Column(JSONB(astext_type=Text()), server_default=text("'[]'::jsonb"))
    maxId = Column(String(256))
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())


class SurveyResponsesArchive(Base):
    __tablename__ = 'survey_responses_archive'

    id = Column(Integer, primary_key=True, server_default=text("nextval('survey_responses_archive_id_seq'::regclass)"))
    solNum = Column(String)
    contemporary_notice_id = Column(Integer)
    response = Column(JSONB(astext_type=Text()), server_default=text("'[]'::jsonb"))
    maxId = Column(String(256))
    original_created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())


t_winston_logs = Table(
    'winston_logs', metadata,
    Column('timestamp', DateTime(True)),
    Column('level', String(255)),
    Column('message', Text),
    Column('meta', JSONB(astext_type=Text()))
)


class Attachment(Base):
    __tablename__ = 'attachment'

    id = Column(Integer, primary_key=True, server_default=text("nextval('attachment_id_seq'::regclass)"))
    notice_id = Column(Integer)
    notice_type_id = Column(ForeignKey('notice_type.id'))
    machine_readable = Column(Boolean)
    attachment_text = Column(Text)
    prediction = Column(Integer)
    decision_boundary = Column(Float(53))
    validation = Column(Integer)
    attachment_url = Column(Text)
    trained = Column(Boolean)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    filename = Column(Text, nullable=False)
    solicitation_id = Column(ForeignKey('solicitations.id'))

    notice_type = relationship('NoticeType')
    solicitation = relationship('Solicitation')


class Notice(Base):
    __tablename__ = 'notice'

    id = Column(Integer, primary_key=True, server_default=text("nextval('notice_id_seq'::regclass)"))
    notice_type_id = Column(ForeignKey('notice_type.id'))
    solicitation_number = Column(String(150), index=True)
    agency = Column(String(150))
    date = Column(DateTime)
    notice_data = Column(JSONB(astext_type=Text()))
    compliant = Column(Integer)
    feedback = Column(JSONB(astext_type=Text()))
    history = Column(JSONB(astext_type=Text()))
    action = Column(JSONB(astext_type=Text()))
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    na_flag = Column(Boolean, default=False)

    notice_type = relationship('NoticeType')
