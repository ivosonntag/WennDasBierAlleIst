import sqlite3


class Dict2Sql(object):
    def __init__(self, path_to_db):
        self.__path_to_db = path_to_db

    def save(self, dictionary, table_name, auto_create=False, auto_flatten=False):
        # handle dictionary and format it if necessary
        dictionary = self.__format_dictionary(dictionary, auto_flatten)

        # check table and change name if necessary
        table_name = self.__check_if_table_with_same_name_and_columns_exists(dictionary, table_name, auto_create)
        if table_name == -1:
            raise Exception("Table with same name but different columns already exists. Couldn't create a new table.")
            return

        # create table if table with same name doesn't exists
        self.__create_table(table_name, dictionary)

        # the actual saving of the data happens here
        con = sqlite3.connect(self.__path_to_db)
        with con:
            query = "insert into '{}' (".format(table_name)
            for key in [*dictionary]:
                query += "{},".format(key)

            # get rid of the last comma
            query = query[:-1]
            query += ") values ("

            for key in [*dictionary]:
                if type(dictionary[key]) is str:
                    tmp = "%r"%dictionary[key]
                    # in sqlite single quotes have to be replaced by double quotes
                    tmp = tmp.replace(r"\'", r"''")
                else:
                    tmp = "'" + str(dictionary[key]) + "'"
                query += "{},".format(tmp)

            # get rid of the last comma
            query = query[:-1]
            query += ")"
            con.execute(query)

        """ Example_
        query = "insert into {} (ID, Text, Sentiment, DateTime)" \
                "values ({}, {}, {}, {})".format(self.hashtag, data['tweet_id'],
                raw_text, data['sentiment'], "%r"%(time.strftime("%Y-%m-%d_%H:%M:%S")))
        """

    def __create_table(self, table_name, dictionary):
        # table doesn't get created if a table with the same name already exists
        query = "create table if not exists '{}' (".format(table_name)
        for key in [*dictionary]:
            query += "'{}' Text,".format(key)

        # get rid of the last comma
        query = query[:-1]
        query += ");"

        con = sqlite3.connect(self.__path_to_db)
        with con:
            con.execute(query)

    def __check_if_table_with_same_name_and_columns_exists(self, dictionary, table_name, auto_create):
        # check if table with the name table_name already exists and compare columns
        # if table already exists with same columns, then the data gets saved in this table
        # if table already exists with different columns and auto_create is true, then the table_name gets a suffix
        con = sqlite3.connect(self.__path_to_db)
        with con:
            # get all table names, returns list of tuples
            tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            # only first element of list
            tables = [i[0].lower() for i in tables]
            tables = sorted(tables, key=str.lower, reverse=True)
            nr = 0
            for table_str in tables:
                # if a table matches name check columns
                if table_str.startswith(table_name.lower()):
                    columns = con.execute("pragma table_info('{}')".format(table_str)).fetchall()
                    column_names = [seq[1] for seq in columns]
                    # compare column_names with keys in dictionary
                    if sorted(column_names) == sorted([*dictionary]):
                        # exact table with same columns already exists -> return table name
                        return table_str
                    else:
                        # table with same name but different columns already exists
                        if auto_create:
                            # auto create new table name by adding "_Nr" to the name. The Nr is incrementing.
                            tmp = table_str.replace(table_name.lower(), "")
                            if len(tmp) > 1 and tmp.find("_") != -1:
                                # increment the nr
                                tmp_nr = int(tmp[1:])
                                nr = max(nr, tmp_nr + 1)
                            else:
                                # if the table name is not like "table_Nr"
                                nr = max(nr, 0)

                        else:
                            # if no auto create -> return -1
                            return -1

            if nr != 0:
                table_name = table_name + "_" + str(nr)
            return table_name

    def __format_dictionary(self, dictionary, auto_flatten):
        # checks data of dictionary for nested lists, array or dictionaries
        # if auto_flatten is true, then lists and arrays are converted to strings. Nested dictionaries are copied
        # in main dictionaries. The keys of the nested dicts getting a prefix.
        sub_dict = dict()
        list_of_deleted_keys = list()
        for key, val in dictionary.items():
            if isinstance(val, dict) or isinstance(val, list) or isinstance(val, tuple):
                # could be a list, tuple or dictionary
                if auto_flatten:
                    if isinstance(val, dict):
                        # if value is a dictionary
                        temp_dict = dict()
                        for tmp_key, tmp_val in val.items():
                            temp_dict[str(key) + "_" + str(tmp_key)] = tmp_val

                        # merging dicts
                        sub_dict = {**sub_dict, **temp_dict}
                    else:
                        # tuples and lists are simply saved as strings
                        dictionary[key] = str(val)
                    list_of_deleted_keys.append(key)
                else:
                    raise Exception("Nested list, array or dictionary detected and auto_flatten is false.")

        for k in list_of_deleted_keys:
            del dictionary[k]

        return {**dictionary, **sub_dict}
