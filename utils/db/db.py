# -*- coding: utf-8 -*-
import json
from sqlalchemy import create_engine, ForeignKeyConstraint, UniqueConstraint, func, case
#from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, \
                       DateTime, Boolean
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from datetime import datetime
from utils.db import db_utils


db_string = db_utils.get_db_url()

Base = declarative_base()

class NoticeType(Base):
    __tablename__ = 'notice_type'
    
    id = Column(Integer, primary_key = True)
    notice_type = Column(String(50), index = True)
    notices = relationship("Notice")
    

class Notice(Base):
    __tablename__ = 'notice'
    
    id = Column(Integer, primary_key=True)
    notice_type_id = Column(Integer, ForeignKey('notice_type.id'))
    notice_number = Column(String(150), index = True)
    date = Column(DateTime, onupdate=datetime.now)
    notice_data = Column(JSONB)
    compliant = Column(Integer)
    action = Column(ARRAY(String(100), dimensions=2))
    attachments = relationship("Attachment", back_populates="notice")
    

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
    

class DataAccessLayer:
    def __init__(self,db_string=db_string):
        self.engine = create_engine(db_string)
        session = sessionmaker()
        session.configure(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.s = session()


    def add_json_nightly_file_to_postgres(self,jsonFile):
        self._add_notice_types()
        for notice_type in jsonFile:
            notice_type_id = self.fetch_notice_type_id(notice_type)
            for x in range(len(jsonFile[notice_type])):
                notice_data = jsonFile[notice_type][x]
                try:
                    attachment_data = notice_data.pop('attachments')
                except KeyError:
                    pass
                compliant = notice_data.pop('compliant')
                notice_number = notice_data.pop('solnbr')
                notice_id = self.fetch_notice_id(notice_number)
                if notice_id:
                    #TODO: fetch the notice based on this ID and update its attribtues
                    pass
                else:
                    postgres_data = Notice(notice_number = notice_number,
                                           notice_data = json.dumps(notice_data),
                                           notice_type_id = notice_type_id,
                                           compliant = compliant)
                try:
                    for attachment in attachment_data:
                        postgres_attachment =  Attachment(prediction = attachment['prediction'],
                                                          decision_boundary = attachment['decision_boundary'],
                                                          attachment_url = attachment['url'],
                                                          attachment_text = attachment['text'],
                                                          validation = attachment['validation'],
                                                          trained = attachment['trained'])
                        postgres_data.attachments.append(postgres_attachment)
                except:
                    #TODO: log the error
                    pass 
                self.s.add(postgres_data)
                self.s.flush()
        self.s.commit()
        
    def _add_notice_types(self):
        for notice_type in ['MOD','COMBINE','PRESOL','AMDCSS','TRAIN']:
            notice_type_id = self.fetch_notice_type_id(notice_type)
            if not notice_type_id:
                n = NoticeType(notice_type=notice_type)
                self.s.add(n)
                self.s.commit()
           
    def add_model_data(self, estimator, best_params):
        '''
        Add model to db.

        Parameters:
            estimator (str): name of the classifier
            best_params (dict): dict of the parameters (best_params_ attribute of classifier instance)
        '''
        postgres_data = Model(estimator = estimator,
                              params = best_params)
        self.s.add(postgres_data)
        self.s.commit()
        
    def get_validation_count(self):
         count = self.s.query(func.count(Attachment.validation))
         total = count.scalar()
         return int(total)

    def get_trained_amount(self):
        sum_of_trained = self.s.query(func.sum(case([(Attachment.trained == True, 1)], else_=0)))
        total = sum_of_trained.scalar()
        return int(total) 
     
    def revalidation_check(self):
        count_of_total_validated = self.get_validation_count()
        sum_of_trained = self.get_trained_amount()
        if (count_of_total_validated - sum_of_trained) > 1000:
            return 1
        else:
            return 0
   
    def query_notice(self,notice):
        #'''need to build out'''
        notice_ID = self.s.query(NoticeType.notice_type).filter(NoticeType.notice_type==notice).first()
        return notice_ID
    
    def get_complaint_amount(self):
        sum_of_compliant = self.s.query(func.sum(Notice.compliant))
        total = sum_of_compliant.scalar()
        return int(total) 
     
    def query_model(self, estimator):
        model = self.s.query(Model.estimator).filter(Model.estimator==estimator).first()
        return model

    def fetch_notice_id(self, notice_number):
        '''
        Fetch the notice id for a given notice_number.

        Parameters:
            notice_number (str): a solicitation number from a notice

        Returns:
            None or notice_id (int): if notice_id, this is the PK for the notice
        '''
        try:
            notice_id = self.s.query(Notice.id).filter(Notice.notice_number==notice_number).first().id
        except AttributeError:
            return
        return notice_id

    def fetch_notice_type_id(self, notice_type):
        '''
        Fetch the notice id for a given notice_number.

        Parameters:
            notice_number (str): a solicitation number from a notice

        Returns:
            None or notice_id (int): if notice_id, this is the PK for the notice
        '''
        try:
            notice_type_id = self.s.query(NoticeType.id).filter(NoticeType.notice_type==notice_type).first().id
        except AttributeError:
            return
        return notice_type_id
        

    def test_relationships(self,notice):
        notice_id = self.s.query(Notice.id).filter(Notice.id==Attachment.notice_id, NoticeType.notice_type==notice).first()
        return notice_id
