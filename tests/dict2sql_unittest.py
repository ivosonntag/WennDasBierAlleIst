import unittest
import os
from utils.dict2sql import Dict2Sql


class TestCreateDB(unittest.TestCase):
    # create sql test database
    def setUp(self):
        self.sql_db = Dict2Sql("TestDB.sqlite")
        self.table_name = "TestTable"
        self.__generate_test_data()

    def tearDown(self):
        os.remove("TestDB.sqlite")
        pass

    def __generate_test_data(self):
        data = []
        for i in range(0, 100):
            dictionary = dict()
            dictionary["key1"] = i
            dictionary["key2"] = None
            dictionary["key3"] = """string 2q' ' \n 3q34 3\t"  %&&"(%)§% Äö ösdpoüp3wr"""
            dictionary["key4"] = False
            data.append(dictionary)

        self.test_data_flat_dictionary = data


class TestInsertData(TestCreateDB):
    def test_insert_std_data(self):
        # insert normal test data
        for data in self.test_data_flat_dictionary:
            self.sql_db.save(data, self.table_name, False, False)

    def test_insert_data_with_different_columns_without_auto_create(self):
        dict1 = {"test1": True}
        self.sql_db.save(dict1, self.table_name, False, False)
        dict2 = {"test2": True}
        with self.assertRaises(Exception):
            self.sql_db.save(dict2, self.table_name, False, False)

    def test_insert_data_with_different_columns_with_auto_create(self):
        dict1 = {"test1": True}
        self.sql_db.save(dict1, self.table_name, False, False)
        dict2 = {"test2": True}
        self.sql_db.save(dict2, self.table_name, True, False)

    def test_insert_nested_dict_without_auto_flatten(self):
        dict1 = {"test1": True}
        self.sql_db.save(dict1, self.table_name, False, False)
        dict2 = {"test1": dict1}
        with self.assertRaises(Exception):
            self.sql_db.save(dict2, self.table_name, True, False)

    def test_insert_nested_dict_with_auto_flatten(self):
        dict1 = {"test1": True}
        dict2 = {"test2": dict1}
        self.sql_db.save(dict2, self.table_name, True, True)


class TestGetData(TestCreateDB):
    def test_get_data_with_string(self):
        # get first two rows
        for data in self.test_data_flat_dictionary:
            self.sql_db.save(data, self.table_name, False, False)

        rows = self.sql_db.get_all_data_with_string_filter(self.table_name, "*", "key1=0 Or key1=1")
        self.assertEqual(2, len(rows))
        rows = self.sql_db.get_all_data_with_string_filter(self.table_name, "*", "key1=0 And key1=1")
        self.assertEqual(0, len(rows))
        rows = self.sql_db.get_all_data_with_string_filter(self.table_name, "key1, key2", "key1=0 Or key1=1")
        self.assertEqual(2, len(rows))
        rows = self.sql_db.get_all_data_with_string_filter(self.table_name, ["key1", "key2"], "key1=0 Or key1=1")
        self.assertEqual(2, len(rows))
        rows = self.sql_db.get_all_data_with_string_filter(self.table_name, {"key1", "key2"}, "key1=0 Or key1=1")
        self.assertEqual(2, len(rows))

    def test_get_data_with_dict(self):
        # get first row
        for data in self.test_data_flat_dictionary:
            self.sql_db.save(data, self.table_name, False, False)

        filter_dict = dict()
        filter_dict["key1"] = 0
        filter_dict["key2"] = "1"
        rows = self.sql_db.get_all_data_with_dict_filter(self.table_name, "*", filter_dict, True)
        self.assertEqual(0, len(rows))
        rows = self.sql_db.get_all_data_with_dict_filter(self.table_name, "*", filter_dict, False)
        self.assertEqual(1, len(rows))


class TestUpdateData(TestCreateDB):
    def test_update_with_string(self):
        # update first 2 rows with string as filter
        for data in self.test_data_flat_dictionary:
            self.sql_db.save(data, self.table_name, False, False)
        set_values = dict()
        set_values["key2"] = """string 2q' ' \n 3q34 3\t"  %&&"(%)§% Äö ösdpoüp3wr"""
        set_values["key4"] = True

        filter_str = "key1='0' or key1=1"
        self.sql_db.update_with_string_filter(set_values, self.table_name, filter_str)

    def test_update_with_dict(self):
        # update first 2 rows with dict as filter
        for data in self.test_data_flat_dictionary:
            self.sql_db.save(data, self.table_name, False, False)
        set_values = dict()
        set_values["key2"] = """string 2q' ' \n 3q34 3\t"  %&&"(%)§% Äö ösdpoüp3wr"""
        set_values["key4"] = True

        filter_dict = dict()
        filter_dict["key1"] = 0
        filter_dict["key2"] = "1"
        self.sql_db.update_with_dict_filter(set_values, self.table_name, filter_dict, False)
        self.sql_db.update_with_dict_filter(set_values, self.table_name, filter_dict, True)


if __name__ == '__main__':
    unittest.main()
