import os
from time import sleep
import sys
import unittest
from pathlib import Path
from utils.db.db_utils import get_db_url, session_scope, DataAccessLayer, insert_data
import pytest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.sam_utils import get_sol_data_from_feed, update_sam_data_feed, update_old_solicitations, \
                            SAM_DATA_FEED_EXISTED, SAM_DATA_FEED_DOWNLOADED, SAM_DATA_FEED_ERROR

import utils.db.db_utils
from utils.db.db import Notice, Predictions, Solicitations


class SamUtilsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @pytest.mark.skip(reason="intermittent fails downloading file")
    def test_update_sam_data_feed(self):
        existing_filename = '/tmp/sam_data_feed.tmp'
        Path(existing_filename).touch()

        new_filename = '/tmp/ContractOpportunitiesFullCSV.csv'
        if os.path.isfile(new_filename):
            os.remove(new_filename)

        assert update_sam_data_feed(existing_filename) == SAM_DATA_FEED_EXISTED

        assert update_sam_data_feed(new_filename, 30) == SAM_DATA_FEED_DOWNLOADED
        assert os.path.isfile(new_filename)
        assert os.path.getsize(new_filename) > 400 * 1000 * 1000  # larger than 400 MB

        assert update_sam_data_feed(new_filename, 30) == SAM_DATA_FEED_EXISTED

    @pytest.mark.skip(reason="intermittent fails downloading file")
    def test_update_old_solicitations(self):
        conn_string = get_db_url()
        dal = DataAccessLayer(conn_string)
        dal.connect()
        with session_scope(dal) as session:
            update_old_solicitations(session)

#
    # def test_get_sol_data_from_feed(self):
    #     sol_data = get_sol_data_from_feed("36C24121Q0028")
    #     assert "SolNum" in sol_data
    #     assert sol_data["SolNum"] == "36C24121Q0028"
    #
    # def test_update_from_sam_feed(self):
    #
    #     count = 0
    #     # first remove all invalid marks
    #     conn_string = get_db_url()
    #     dal = DataAccessLayer(conn_string)
    #     dal.connect()
    #     with session_scope(dal) as session:
    #         stmt = session.query(Solicitations).filter(Solicitations.active.is_(False)).update({"active" : True})
    #         session.commit()
    #
    #         update_old_solicitations(session, age_cutoff=7, max_updates=200)
    #
    #         # we should now have a bunch of inactive solicitations
    #         count = session.query(Solicitations).filter(Solicitations.active.is_(False)).count()
    #
    #     assert count > 0
    #
    #
    # def test_update_from_sam_feed_date(self):
    #
    #     # first remove all invalid marks
    #     conn_string = get_db_url()
    #     dal = DataAccessLayer(conn_string)
    #     dal.connect()
    #     with session_scope(dal) as session:
    #         stmt = session.query(Solicitations).filter(Solicitations.active.is_(False)).update({"active": True})
    #         session.commit()
    #
    #         update_old_solicitations(session, age_cutoff=36500, max_updates=1000)
    #
    #         # There shouldn't be any solicitations that are 100 years old
    #         count = session.query(Solicitations).filter(Solicitations.active.is_(False)).count()
    #
    #     assert count == 0
    #
    #
    # def test_update_from_sam_feed_updatedAt(self):
    #
    #     conn_string = get_db_url()
    #     dal = DataAccessLayer(conn_string)
    #     dal.connect()
    #     with session_scope(dal) as session:
    #         # first remove all invalid marks
    #         stmt = session.query(Solicitations).filter(Solicitations.active.is_(False)).update({"active": True})
    #         session.commit()
    #
    #         before_pred = session.query(Predictions).order_by(Predictions.updatedAt).first()
    #         before_date = before_pred.updatedAt
    #
    #         update_old_solicitations(session, age_cutoff=10, max_updates=200)
    #
    #         after_pred = session.query(Predictions).order_by(Predictions.updatedAt.desc()).first()
    #         after_date = after_pred.updatedAt
    #
    #
    #     print (before_pred)
    #     print(after_pred)
    #
    #     assert after_date > before_date
    #
    # def test_stats_for_update(self):
    #     max_updates = 500
    #
    #     conn_string = get_db_url()
    #     dal = DataAccessLayer(conn_string)
    #     dal.connect()
    #     with session_scope(dal) as session:
    #         # first remove all invalid marks
    #         stmt = session.query(Solicitations).filter(Solicitations.active.is_(False)).update({"active": True})
    #         session.commit()
    #
    #         stats = update_old_solicitations(session, age_cutoff=0, max_updates=max_updates)
    #         all_predictions_examined = session.query(Predictions.id).count()
    #         actual_updated_count = session.query(Solicitations.filter(Solicitations.active == False)).count()
    #
    #
    #
    #     assert stats['examined'] == max_updates+1
    #     assert stats['examined'] < stats['updated']
    #     assert actual_updated_count == stats['updated']
    #


if __name__ == '__main__':
    unittest.main()