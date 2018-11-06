from sqlalchemy import create_engine, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, \
                       Date, Boolean, Sequence, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from config import SQLALCHEMY_URI

Base = declarative_base()

class DataAccessLayer:

    def __init__(self):
        self.engine = None
        self.conn_string = SQLALCHEMY_URI

    def connect(self):
        self.engine = create_engine(self.conn_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

dal = DataAccessLayer()

class NoticeType(Base):
    __tablename__ = 'notice_type'
    
    id = Column(Integer, primary_key = True)
    notice_type = Column(String(50))
    # specify a bidirectional one-to-many relationship with the child table, Notice
    notices = relationship("Notice", back_populates="notice_type")
    

class Notice(Base):
    __tablename__ = 'notice'
    
    id = Column(Integer, primary_key=True)
    notice_type_id = Column(Integer, ForeignKey('notice_type.id'))
    notice_data = Column(JSONB)
    date = Column(Date)
    # specify a bidirectional one-to-many relationship with the parent table, NoticeType
    notice_types = relationship("NoticeType", back_populates="notice")

    

class Attachment(Base):
    __tablename__ = 'attachment'
    
    id = Column(Integer, primary_key = True)
    validation_id = Column(Integer, ForeignKey('respondent.id'))
    notice_id = Column(Integer, ForeignKey('survey.id'))
    notice_type_id = Column(Integer, ForeignKey('question.id'))
    
    attachment_data = Column(JSONB)
    
    version_predictions = relationship("VersionPrediction")  

    
class Model(Base):
    
    __tablename__ = 'model'
    
    id = Column(Integer, primary_key = True)
    description = Column(String(100))
    
    versions = relationship("Version")

    
class Version(Base):
    
    __tablename__ = "version"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('model.id'))
    create_date = Column(Date)
    end_date = Column(Date, nullable=True)
    parameters = Column(JSONB)
    resuts = Column(JSONB)
    
    predictions = relationship("VersionPrediction", back_populates="version")
    

class Prediction(Base):
    
    __tablename__ = 'prediction'
    
    id = Column(Integer, primary_key = True)
    prediction = Column(Integer)
    
    versions = relationship("VersionPrediction", back_populates="prediction")
    

class VersionPrediction(Base):
    '''
    Bi-directional association table for many-to-many relationship b/w Version and Prediction.
    '''
    __tablename__ = 'version_prediction'

    model_id = Column(Integer, ForeignKey('model.id', primary_key = True))
    version_id = Column(Integer, ForeignKey('version.id'), primary_key = True)
    prediction_id = Column(Integer, ForeignKey('prediction.id'), primary_key = True)
    attachment_id = Column(Integer, ForeignKey('response.id'), primary_key = True)
    validation_id = Column(Integer, ForeignKey('validation.id'), primary_key = True)
    notice_id = Column(Integer, ForeignKey('notice.id'), primary_key = True)
    notice_type_id = Column(Integer, ForeignKey('notice_type.id'), primary_key = True)

    version = relationship("Version", back_populates="predictions")
    prediction = relationship("Prediction", back_populates="versions")


class Validation(Base):
    
    __tablename__ = 'validation'
    
    id = Column(Integer, primary_key = True)
    validation = Column(Integer, nullable = True)
    
    responses = relationship("Response")
