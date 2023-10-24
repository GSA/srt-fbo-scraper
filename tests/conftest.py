import pytest
from fbo_scraper.db.connection import TestDAL


@pytest.fixture(scope="class")
def db_class(request):
    
    # set a class attribute on the invoking test context
    request.cls.dal = TestDAL()

@pytest.fixture()
def db_access_layer():

    dal = TestDAL()
    dal.create_test_postgres_db()
    dal.connect()

    return dal