import os
import sys
import unittest
from unittest.mock import patch
import pytest
import logging
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )

from fbo_scraper.db.db_utils import session_scope, DataAccessLayer, clear_data
from fbo_scraper.db.connection import get_db_url

from sqlalchemy.orm.session import close_all_sessions

def test_end_to_end(db_access_layer):

    logger = logging.getLogger("fbo_scraper.db.db_utils")


    with patch('fbo_scraper.main.setup_db', return_value=db_access_layer) as mock_dal:
        from fbo_scraper.main import main

        with patch.object(logger, 'error', wraps=logger.error):
            main(limit = 20)
            assert logger.error.call_count == 0
    

if __name__ == '__main__':
    unittest.main()