import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, \
                       DateTime, Boolean, Float, MetaData, inspect
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY



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
    createdAt = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)
    updatedAt = Column(DateTime, nullable = True)
    na_flag = Column(Boolean, default = False)

class NoticeType(Base):
    __tablename__ = 'notice_type'
    id = Column(Integer, primary_key = True)
    notice_type = Column(String(50), index = True)

class Attachment(Base):
    __tablename__ = 'attachment'
    id = Column(Integer, primary_key = True)
    notice_id = Column(Integer)  #Column(Integer, ForeignKey('notice.id'))
    notice_type_id = Column(Integer, ForeignKey('notice_type.id'))
    filename = Column(Text, nullable = False)
    machine_readable = Column(Boolean)
    attachment_text = Column(Text, nullable = True)
    prediction = Column(Integer, nullable = True)
    decision_boundary = Column(Float, nullable = True)
    validation = Column(Integer, nullable = True)
    attachment_url = Column(Text)
    trained = Column(Boolean, nullable = True)
    createdAt = Column(DateTime, nullable = False, default=datetime.datetime.utcnow)
    updatedAt = Column(DateTime, nullable = True)
    solicitation_id = Column(Integer, ForeignKey('solicitations.id'))
    solicitaiton = relationship("Solicitation", back_populates = "attachments")

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
    createdAt = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)
    updatedAt = Column(DateTime, nullable = False)

class Agencies(Base):
    __tablename__ = 'Agencies'
    id = Column(Integer, primary_key = True)
    agency = Column(String)
    acronym = Column(String)
    createdAt = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)
    updatedAt = Column(DateTime, nullable = False)

class AgencyAlias(Base):
    __tablename__ = "agency_alias"
    id = Column(Integer, primary_key = True)
    agency_id = Column(Integer)
    alias = Column(String)
    createdAt = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)
    updatedAt = Column(DateTime, nullable = False)

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
    createdAt = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)
    updatedAt = Column(DateTime, nullable = False)

class Predictions(Base):
    __tablename__ = 'Predictions'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)
    agency = Column(String)
    numDocs = Column(Integer)
    solNum = Column(String)
    noticeType = Column(String)
    date = Column(DateTime)
    office = Column(String)
    na_flag = Column(Boolean)
    category_list = Column(JSONB)
    undetermined = Column(Boolean)
    action = Column(JSONB)
    actionStatus= Column(String)
    actionDate = Column(DateTime)
    feedback = Column(JSONB)
    history = Column(JSONB)
    contactInfo = Column(JSONB)
    parseStatus = Column(JSONB)
    predictions = Column(JSONB)
    reviewRec = Column(String)
    searchText = Column(String)
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)

class Solicitation(Base):
    __tablename__ = 'solicitations'
    id = Column(Integer, primary_key=True)
    solNum = Column(String)
    active = Column(Boolean)
    createdAt = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)
    updatedAt = Column(DateTime, nullable = False)
    title = Column(String)
    url = Column(String)
    agency = Column(String)
    agency_id = Column(Integer)
    numDocs = Column(Integer)
    notice_type_id = Column(Integer)
    noticeType = Column(String)
    date = Column(DateTime)
    office = Column(String)
    na_flag = Column(Boolean)
    category_list = Column(JSONB)
    undetermined = Column(Boolean)
    history = Column(JSONB)
    action = Column(JSONB)
    actionStatus = Column(String)
    actionDate = Column(DateTime)
    contactInfo= Column(JSONB)
    parseStatus = Column(JSONB)
    predictions = Column(JSONB)
    reviewRec = Column(String)
    searchText = Column(String)
    compliant = Column (Integer)
    noticeData = Column(JSONB)
    attachments = relationship("Attachment", back_populates="solicitaiton", cascade="all, delete-orphan");


