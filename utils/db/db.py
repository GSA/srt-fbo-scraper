from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, \
                       DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from datetime import datetime

Base = declarative_base()


class Notice(Base):
    __tablename__ = 'notice'
    
    id = Column(Integer, primary_key=True)
    notice_type_id = Column(Integer, ForeignKey('notice_type.id'))  
    notice_number = Column(String(150), index = True)
    agency = Column(String(150))
    date = Column(DateTime, onupdate=datetime.now)
    notice_data = Column(JSONB)
    compliant = Column(Integer)
    action = Column(ARRAY(String(100), dimensions=2))
    attachments = relationship("Attachment", back_populates="notice")
    notice_type = relationship("NoticeType", back_populates="notices")
    
class NoticeType(Base):
    __tablename__ = 'notice_type'
    
    id = Column(Integer, primary_key = True)
    notice_type = Column(String(50), index = True)
    notices = relationship("Notice", back_populates = 'notice_type')

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
    




    
