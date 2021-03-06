import unittest
import uuid
from ballot_box import settings
from ballot_box.data.models import DataItem, DataType
from ballot_box.modules import api
from ballot_box.data.demo_repository import DemoRepository


class TestDemoRepository(unittest.TestCase):
    def setUp(self):
        """Call before every test case.
        Do not use a live database for this it will delete mess up your data.
        """



        self.db = DemoRepository(settings.DB_TEST_CONNECTION_STRING)
        self.data_type  = self.db.get_data_type("Test")
        if not self.data_type:
            self.data_type = DataType(key="Test")
            self.db.insert(self.data_type)

        self.clearData()
        self.db.commit()

    def tearDown(self):
        """call after every test case."""
        self.db.end_session()

    def get_contest_id(self):
        return api.ballot_list_contests()['result'][0]

    def get_decision_id(self):
        return api.ballot_list_decisions()['result'][0]

    def get_voter_id(self):
        return api.ballot_get_decision(self.get_decision_id())['result']['voter_id']

    def clearData(self):
        self.db.db_session.execute('delete from data_item_map')
        self.db.db_session.execute('delete from data_item')
        self.db.commit()


    def test_insert_item(self):
        id = str(uuid.uuid4())
        item = DataItem(key=id, value='test', data_type_key="Test")
        self.db.insert(item)

        for i in range(1, 3):
            id = str(uuid.uuid4())
            child = DataItem(key=id, value='test{0}'.format(i), data_type_key="Test", sort=i)
            item.children.append(child)

        self.db.commit()

        result = self.db.get_item(id)
        print(result)
        self.assertIsNotNone(result)
        return result

    def test_debug_load_demo_contests(self):
        self.db._debug_load_demo_contests()
        self.db.commit()
        contests = self.db.get_all_contests()
        print(contests)
        self.assertTrue(len(contests) > 0 )

    def test_get_items_by_data_type(self):
        self.test_insert_item()
        result = self.db.get_items_by_data_type("Test")
        print(result)
        self.assertTrue(len(result) > 0)


    def test_get_contest_decisions(self):
        contest = self.db._api_get_contest_by_id(self.get_contest_id())
        results = self.db.get_contest_decisions(contest)
        self.assertTrue(len(results) > 0 )



    def test_get_items_by_value(self):
        self.test_insert_item()
        result = self.db.get_items_by_value('test', "Test")
        print(result)
        self.assertTrue(len(result) > 0)

    def test_get_voter_contest_ids(self):
        result = self.db.get_voter_contest_ids(self.get_voter_id())
        print(result)
        self.assertTrue(len(result) > 0)
        #test a bad voter id
        result = self.db.get_voter_contest_ids('asdfasdfa')
        print(result)
        self.assertFalse(result)


