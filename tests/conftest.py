import pytest
from fbo_scraper.db.db_utils import DataAccessLayer
from sqlalchemy_utils import database_exists, create_database, drop_database
import getpass

class TestDB(DataAccessLayer):

        def __init__(self):
            self._username = "circleci"
            self._password = "srtpass"
            conn_string = f"postgresql+psycopg2://{self.username}:{self.password}@localhost/test"
            super().__init__(conn_string)
        

        @property
        def username(self):
            if self._username is None:
                self._username = getpass.getuser()
            return self._username

        @property
        def password(self):
            if self._password is None:
                self._password = getpass.getpass()
            return self._password

        def drop_test_postgres_db(self):
            if database_exists(self.conn_string):
                drop_database(self.conn_string)

        def create_test_postgres_db(self):
            if not database_exists(self.conn_string):
                create_database(self.conn_string, template="template_srt")

@pytest.fixture(scope="class")
def db_class(request):
    
    # set a class attribute on the invoking test context
    request.cls.dal = TestDB()

@pytest.fixture()
def db_access_layer():

    dal = TestDB()
    dal.create_test_postgres_db()
    dal.connect()

    return dal