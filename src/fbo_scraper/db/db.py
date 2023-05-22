import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, \
                       DateTime, Boolean, Float, MetaData, inspect, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func


def now_minus_two():
    '''
    A callable to be used with the default kwarg in a Column constructor.

    Returns:
        A datetime object containing the day before yesterday's date
    '''
    return datetime.datetime.utcnow() - datetime.timedelta(2)

#see https://docs.sqlalchemy.org/en/latest/core/constraints.html#constraint-naming-conventions
meta = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
      })
Base = declarative_base(metadata=meta)

class Notice(Base):
    __tablename__ = 'notice'
    id = Column(Integer, primary_key = True)
    notice_type_id = Column(Integer, ForeignKey('notice_type.id'))
    solicitation_number = Column(String(150), index = True)
    agency = Column(String(150))
    date = Column(DateTime, default = now_minus_two)
    notice_data = Column(JSONB)
    compliant = Column(Integer)
    feedback = Column(JSONB)
    history = Column(JSONB)
    action = Column(JSONB)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, nullable = True, onupdate=func.now())
    na_flag = Column(Boolean, default = False)

class NoticeType(Base):
    __tablename__ = 'notice_type'
    id = Column(Integer, primary_key = True)
    notice_type = Column(String(50), index = True)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())

class Attachment(Base):
    __tablename__ = 'attachment'
    id = Column(Integer, primary_key = True)
    notice_id = Column(Integer)  #Column(Integer, ForeignKey('notice.id'))
    notice_type_id = Column(Integer, ForeignKey('notice_type.id'))
    filename = Column(Text, nullable = False)
    machine_readable = Column(Boolean)
    attachment_text = Column(Text)
    prediction = Column(Integer)
    decision_boundary = Column(Float(53))
    validation = Column(Integer)
    attachment_url = Column(Text)
    trained = Column(Boolean)
    createdAt = Column(DateTime, nullable = False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    solicitation_id = Column(Integer, ForeignKey('solicitations.id'))

    notice_type = relationship('NoticeType')
    solicitation = relationship("Solicitation", back_populates = "attachments")

class Model(Base):
    __tablename__ = 'model'
    id = Column(Integer, primary_key = True)
    results = Column(JSONB)
    params = Column(JSONB)
    score = Column(Float)
    create_date = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)

class Users(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key = True)
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

class Agencies(Base):
    __tablename__ = 'Agencies'
    id = Column(Integer, primary_key = True)
    agency = Column(String)
    acronym = Column(String)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())

class AgencyAlias(Base):
    __tablename__ = "agency_alias"
    id = Column(Integer, primary_key = True)
    agency_id = Column(Integer)
    alias = Column(String)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())


class Surveys(Base):
    __tablename__ = 'Surveys'
    id = Column(Integer, primary_key = True)
    question = Column(Text)
    choices = Column(JSONB)
    section = Column(String(2000))
    type = Column(String(2000))
    answer = Column(Text)
    note = Column(Text)
    choicesNote = Column(JSONB)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())

class Predictions(Base):
    __tablename__ = 'Predictions'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String)
    agency = Column(String)
    numDocs = Column(Integer)
    solNum = Column(String, nullable=False, unique=True)
    noticeType = Column(String)
    date = Column(DateTime)
    office = Column(String)
    na_flag = Column(Boolean)
    eitLikelihood = Column(JSONB)
    undetermined = Column(Boolean)
    action = Column(JSONB)
    actionStatus= Column(String)
    actionDate = Column(DateTime)
    history = Column(JSONB)
    contactInfo = Column(JSONB)
    parseStatus = Column(JSONB)
    predictions = Column(JSONB)
    reviewRec = Column(String)
    searchText = Column(String)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    active = Column(Boolean, server_default=text("true"))

class Solicitation(Base):
    __tablename__ = 'solicitations'
    id = Column(Integer, primary_key=True)
    solNum = Column(String, nullable=False, unique=True)
    active = Column(Boolean, server_default=text("true"))
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    title = Column(String)
    url = Column(String)
    agency = Column(String)
    agency_id = Column(Integer)
    numDocs = Column(Integer)
    notice_type_id = Column(Integer)
    noticeType = Column(String)
    date = Column(DateTime)
    office = Column(String)
    na_flag = Column(Boolean, server_default=text("false"))
    category_list = Column(JSONB)
    undetermined = Column(Boolean)
    history = Column(JSONB, server_default=text("'[]'::jsonb"))
    action = Column(JSONB, server_default=text("'[]'::jsonb"))
    actionStatus = Column(String)
    actionDate = Column(DateTime)
    contactInfo= Column(JSONB)
    parseStatus = Column(JSONB)
    predictions = Column(JSONB, server_default=text("'{\"value\": \"red\", \"history\": []}'::jsonb"))
    reviewRec = Column(String)
    searchText = Column(String)
    compliant = Column(Integer, server_default=text("0"))
    noticeData = Column(JSONB)
    
    attachments = relationship("Attachment", back_populates="solicitation", cascade="all, delete-orphan");

class SurveyResponse(Base):
    __tablename__ = 'survey_responses'

    id = Column(Integer, primary_key=True)
    solNum = Column(String, index=True)
    contemporary_notice_id = Column(Integer)
    response = Column(JSONB(astext_type=Text()), server_default=text("'[]'::jsonb"))
    maxId = Column(String(256))
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())

class SurveyResponsesArchive(Base):
    __tablename__ = 'survey_responses_archive'

    id = Column(Integer, primary_key=True)
    solNum = Column(String)
    contemporary_notice_id = Column(Integer)
    response = Column(JSONB(astext_type=Text()), server_default=text("'[]'::jsonb"))
    maxId = Column(String(256))
    original_created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())

t_survey_backup = Table(
    'survey_backup', meta,
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

t_winston_logs = Table(
    'winston_logs', meta,
    Column('timestamp', DateTime(True)),
    Column('level', String(255)),
    Column('message', Text),
    Column('meta', JSONB(astext_type=Text()))
)

t_sequelize_meta = Table(
    'SequelizeMeta', meta,
    Column('name', String(255), primary_key=True)
    )