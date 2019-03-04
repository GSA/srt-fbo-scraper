from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, \
                       DateTime, Boolean, Float, MetaData, inspect
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
import datetime


def now_minus_two():
    '''
    A callable to be used with the default kwarg in a Column constructor.

    Returns:
        A datetime object containing the day before yesterday's date
    '''
    return datetime.datetime.now() - datetime.timedelta(2)

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
    id = Column(Integer, primary_key=True)
    notice_type_id = Column(Integer, ForeignKey('notice_type.id'))
    solicitation_number = Column(String(150), index = True)
    agency = Column(String(150))
    date = Column(DateTime, default=now_minus_two)
    notice_data = Column(JSONB)
    compliant = Column(Integer)
    action = Column(ARRAY(String(100), dimensions=2))
    attachments = relationship("Attachment", back_populates="notice")

class NoticeType(Base):
    __tablename__ = 'notice_type'
    id = Column(Integer, primary_key=True)
    notice_type = Column(String(50), index = True)

class Attachment(Base):
    __tablename__ = 'attachment'
    id = Column(Integer, primary_key = True)
    notice_id = Column(Integer, ForeignKey('notice.id'))
    notice_type_id = Column(Integer, ForeignKey('notice_type.id'))
    machine_readable = Column(Boolean)
    attachment_text = Column(Text, nullable=True)
    prediction = Column(Integer, nullable=True)
    decision_boundary = Column(Float, nullable=True)
    validation = Column(Integer, nullable=True)
    attachment_url = Column(Text)
    trained = Column(Boolean, nullable=True)
    notice = relationship("Notice", 
                          back_populates="attachments")

class Model(Base):
    __tablename__ = 'model'
    id = Column(Integer, primary_key = True)
    results = Column(JSONB)
    params = Column(JSONB)
    score = Column(Float)
    create_date = Column(DateTime, default=datetime.datetime.now)

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
    createdAt = Column(DateTime, nullable = False)
    updatedAt = Column(DateTime, nullable = False)

class Agencies(Base):
    __table__name = 'Agencies'
    id = Column(Integer, primary_key = True)
    agency = Column(String)
    acronym = Column(String)
    createdAt = Column(DateTime, nullable = False)
    updatedAt = Column(DateTime, nullable = False)



