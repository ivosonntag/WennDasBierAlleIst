import os

from utils.data_storage import DataStorage
from utils.helper_functions import create_db_connection


class DataSQL(DataStorage):
    """Implementation of abstract DataStorage Class
    """

    def __init__(self, hashtag, config):
        self._set_data(hashtag, config)

        # if database doesn't exist under this path it will be created automatically
        dir_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), self._path)
        database_name = config.get('MAIN', 'db_name')
        self.__path_to_file = dir_name + database_name

        self.__table_name = self.__check_if_exakt_table_with_hashtag_as_name_exists()
        self.__create_table()

    def save(self, data):
        conn = create_db_connection(self.__path_to_file)
        with conn:
            query = "insert into '{}' (".format(self.__table_name)
            for key in self._list_of_keys:
                query += "{},".format(key)

            # get rid of the last comma
            query = query[:-1]
            query += ") values ("

            for key in self._list_of_keys:
                if type(data[key]) is str:
                    tmp = "%r"%data[key]
                    # in sqlite single quotes have to be replaced by double quotes
                    tmp = tmp.replace(r"\'", r"''")
                else:
                    tmp = "'" + str(data[key]) + "'"
                query += "{},".format(tmp)

            # get rid of the last comma
            query = query[:-1]
            query += ")"
            conn.execute(query)

        """
        OLD:
        query = "insert into {} (ID, Text, Sentiment, DateTime)" \
                "values ({}, {}, {}, {})".format(self.hashtag, data['tweet_id'],
                raw_text, data['sentiment'], "%r"%(time.strftime("%Y-%m-%d_%H:%M:%S")))
        """

    def get_info(self):
        return self.__path_to_file

    def __check_if_exakt_table_with_hashtag_as_name_exists(self):
        # if yes return the table name
        # if no return the new table name
        con = create_db_connection(self.__path_to_file)
        with con:
            # get all tables
            nr = 0
            tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            for row in tables:
                # if a table matches hashtag check columns
                table_str = str(row[0]).lower()
                if table_str.startswith(self._hashtag.lower()):
                    colums = con.execute("pragma table_info('{}')".format(table_str)).fetchall()
                    colum_names = [seq[1] for seq in colums]
                    # compare colum_names with list in config file
                    if sorted(colum_names) == self._list_of_keys:
                        return table_str
                    else:
                        tmp = table_str.rfind("_")
                        if tmp != -1:
                            tmp = table_str[tmp+1:]
                        max(nr, int(tmp))
                        nr += 1
            return self._hashtag + '_' + str(nr)

    def __create_table(self):
        # table doesn't get created if a table with the same name already exists

        query = "create table if not exists '{}' (".format(self.__table_name)
        for key in self._list_of_keys:
            query += "'{}' Text,".format(key)

        # get rid of the last comma
        query = query[:-1]
        query += ");"

        con = create_db_connection(self.__path_to_file)
        with con:
            con.execute(query)

        """
        OLD:
        query = "create table if not exists{} ("\
            "'ID' TEXT NOT NULL,"\
            "'Text' TEXT,"\
            "'Sentiment' REAL,"\
            "'DateTime' TEXT"\
            ");".format(self.name)
            "PRIMARY KEY('ID')"\
        """
