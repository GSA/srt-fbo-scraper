# -*- coding: utf-8 -*-
import psycopg2 , json
from sqlalchemy import create_engine, ForeignKeyConstraint, UniqueConstraint
#from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, \
                       Date, Boolean, Sequence, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from utils.db import db_utils


db_string = db_utils.get_db_url()
now = datetime.now()
current_time = now.strftime("%Y-%m-%d")


Base = declarative_base()

class NoticeType(Base):
    __tablename__ = 'notice_type'
    
    id = Column(Integer, primary_key = True)
    notice_type = Column(String(50))
    # specify a bidirectional one-to-many relationship with the child table, Notice
    notices = relationship("Notice")
    

class Notice(Base):
    __tablename__ = 'notice'
    
    id = Column(Integer, primary_key=True)
    notice_type_id = Column(Integer, ForeignKey('notice_type.id'))
    notice_data = Column(JSONB)
    date = Column(Date)
    noncompliant = Column(Integer)
    #attachment_id = Column(Integer, ForeignKey('attachment.id'))
    # specify a bidirectional one-to-many relationship with the parent table, NoticeType
    #notice_types = relationship("NoticeType", back_populates="notices")
    attachments = relationship("Attachment", back_populates="notice_data")
    

class Attachment(Base):
    __tablename__ = 'attachment'
    
    id = Column(Integer, primary_key = True)
    #validation_id = Column(Integer, ForeignKey('respondent.id'))
    notice_id = Column(Integer, ForeignKey('notice.id'))
    #notice_type_id = Column(Integer, ForeignKey('question.id'))   
    prediction = Column(Integer)
    decision_boundary = Column(Integer)
    attachment_text = Column(Text)
    attachment_url = Column(Text)
    validation = Column(Integer, nullable=True)
    trained = Column(Boolean, nullable=True)
    notice_data = relationship("Notice", back_populates="attachments")



class DataAccessLayer:
    def __init__(self):
        self.engine = create_engine(db_string)
        session = sessionmaker()
        session.configure(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.s = session()


    def add_json_nightly_file_to_postgres(self,jsonFile):
        self._add_notice_db()
        for notice in jsonFile:
            noticeID = self.s.query(NoticeType.id).filter(NoticeType.notice_type==notice).first()
            #n = NoticeType(notice_type=notice)
            for x in range(len(jsonFile[notice])):
                notice_data = jsonFile[notice][x]
                try:
                    attachment_data = notice_data.pop('attachments')
                except KeyError:
                    pass
                non_compliant =notice_data.pop('noncompliant')
                postgres_data = Notice(notice_data=json.dumps(notice_data),notice_type_id=noticeID,date=current_time,noncompliant=non_compliant)
                try:
                    for attachment in attachment_data:
                        postgres_attachment =  Attachment(prediction=attachment['prediction'],decision_boundary=attachment['decision_boundary'],attachment_url = attachment['url'],attachment_text=attachment['text'])
                        postgres_data.attachments.append(postgres_attachment)
                except:
                    pass # we should log the errors when it acually fails
                self.s.add(postgres_data)
                self.s.flush()
        self.s.commit()
        
    def _add_notice_db(self):
       try:
           if self.s.query(Notice).one_or_none() is None:
               for notice in [ 'MOD','COMBINE','PRESOL','AMDCSS']:
                   n = NoticeType(notice_type=notice)
                   self.s.add(n)
               self.s.commit()
       except:
           print("appending data into database")