from abc import ABC, abstractmethod
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .db import Base
from sqlalchemy_utils import database_exists, create_database, drop_database
import logging
logger = logging.getLogger(__name__)

import sys
import os

def get_db_url():
    """
    Return the db connection string depending on the environment
    """
    if os.getenv('VCAP_SERVICES'):
        db_string = os.getenv('DATABASE_URL')
        # SQLAlchemy 1.4 removed the deprecated postgres dialect name, the name postgresql must be used instead now.
        if db_string and db_string.startswith("postgres://"):
            db_string = db_string.replace("postgres://", "postgresql://", 1)
    elif os.getenv('TEST_DB_URL'):
        db_string = os.getenv('TEST_DB_URL')
    else:
        if not os.getenv("VCAP_APPLICATION"):
            db_string = "postgresql+psycopg2://localhost/test"
        else:
            db_string = None
    if db_string:
        return db_string
    else:
        logger.critical("Exception occurred getting database url")
        sys.exit(1)


class DALException(Exception):
    pass

class AbstractDAL(ABC):
    """
    Abstract class for database access layer
    """
    _masked_conn_string = None  

    def __init__(self, connection_string: str = None) -> None:
        self.engine = None
        self._conn_string = connection_string
        self.session = None

    @abstractmethod
    def conn_string(self):
        raise NotImplementedError

    def connect(self):
        raise NotImplementedError('Should not use Abstract Class to Connect')
    
    def disconnect(self):
        raise NotImplementedError('Should not use Abstract Class to Disconnect')

class DataAccessLayer(AbstractDAL):
    """
    Creates an database connection and session factory.
    """

    @property
    def conn_string(self) -> str:
        if self._conn_string is None:
            self._conn_string = get_db_url()
        return self._conn_string

    @property
    def masked_conn_string(self) -> str:
        """
        Return a connection string with the password masked.
        """
        if self._masked_conn_string is None and self.conn_string:
            self._masked_conn_string = self.conn_string.replace(
                    self.conn_string.split(":")[2].split("@")[0], "********")
        return self._masked_conn_string

    def setup_engine(self):
        """
        Setup connection to the database.
        """
        try:
            # Pool_pre_ping description: https://docs.sqlalchemy.org/en/20/core/pooling.html#dealing-with-disconnects
            self.engine = create_engine(self.conn_string, echo=False, pool_pre_ping=True)
        except Exception as e:
            raise DALException(f"Exception occurred creating database engine with uri: {self.masked_conn_string}") from e

    def connect(self):
        """ 
        Setup connection to the database.
        """
        self.setup_engine()
        try:
            self.Session = sessionmaker(self.engine)
            logger.info(f"Connected to database: {self.masked_conn_string}")
        except Exception as e:
            raise DALException(f"Exception occurred creating database session with uri: {self.masked_conn_string}") from e
    
    def disconnect(self):
        """
        Disconnect from the database.
        """
        self.engine.dispose()
        self.engine = None
        self.Session = None

class TestDAL(DataAccessLayer):
    """
    Creates a database connection and session specifically for testing.
    """

    def __init__(self):
            self._username = "circleci"
            self._password = "srtpass"
            conn_string = f"postgresql+psycopg2://{self.username}:{self.password}@localhost/test"
            super().__init__(conn_string)

    @property
    def username(self):
        if self._username is None:
            self._username = input("Enter PostgreSQL username: ")
        return self._username

    @property
    def password(self):
        if self._password is None:
            self._password = input("Enter PostgreSQL password: ")
        return self._password

    def connect(self):
        self.create_test_postgres_db()
        self.setup_engine()
        try:
            Base.metadata.create_all(self.engine)
        except Exception as e:
            logger.critical(
                f"Exception occurred creating database metadata with uri:  \
                               {self.conn_string}. Full traceback here:  {e}",
                exc_info=True,
            )
            sys.exit(1)
        
        self.Session = sessionmaker(self.engine)

    def drop_test_postgres_db(self):
        if database_exists(self.conn_string):
            drop_database(self.conn_string)

    def create_test_postgres_db(self):
        if not database_exists(self.conn_string):
            create_database(self.conn_string)