# -*- coding: utf-8 -*-
from sqlalchemy import create_engine, ForeignKeyConstraint, UniqueConstraint, func, case
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, \
                       DateTime, Boolean
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from datetime import datetime
from utils.db.db_utils import get_db_url

Base = declarative_base()

conn_string = get_db_url()

class DataAccessLayer:

    def __init__(self, conn_string):
        self.engine = None
        self.conn_string = conn_string

    def connect(self):
        self.engine = create_engine(self.conn_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

dal = DataAccessLayer(conn_string)

association_table = Table('association', Base.metadata,
    Column('notice_id', Integer, ForeignKey('notice.id')),
    Column('notice_type_id', Integer, ForeignKey('notice_type.id'))
)

    
class Notice(Base):
    __tablename__ = 'notice'
    
    id = Column(Integer, primary_key=True)
    notice_number = Column(String(150), index = True)
    agency = Column(String(150))
    date = Column(DateTime, onupdate=datetime.now)
    notice_data = Column(JSONB)
    compliant = Column(Integer)
    action = Column(ARRAY(String(100), dimensions=2))
    attachments = relationship("Attachment", back_populates="notice")
    notice_types = relationship("NoticeType", 
                                secondary = association_table, 
                                back_populates = 'notices')
    
class NoticeType(Base):
    __tablename__ = 'notice_type'
    
    id = Column(Integer, primary_key = True)
    notice_type = Column(String(50), index = True)
    notices = relationship("Notice",
                           secondary = association_table,
                           back_populates = 'notice_types')

class Attachment(Base):
    __tablename__ = 'attachment'
    
    id = Column(Integer, primary_key = True)
    notice_id = Column(Integer, ForeignKey('notice.id'))
    notice_type_id = Column(Integer, ForeignKey('notice_type.id'))   
    attachment_text = Column(Text)
    prediction = Column(Integer)
    decision_boundary = Column(Integer)
    validation = Column(Integer, nullable=True)
    attachment_url = Column(Text)
    trained = Column(Boolean, nullable=True)
    notice = relationship("Notice", back_populates="attachments")


class Model(Base):
    __tablename__ = 'model'
    
    id = Column(Integer, primary_key = True)
    estimator = Column(String(50))
    params = Column(JSONB)
    create_date = Column(DateTime, onupdate=datetime.now)
    




    
