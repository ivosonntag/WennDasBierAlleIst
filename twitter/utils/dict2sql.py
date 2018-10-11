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
                tmp = self.__format_string_sql_friendly(dictionary[key])
                query += "{},".format(tmp)

            # get rid of the last comma
            query = query[:-1]
            query += ")"
            con.execute(query)

    def update_with_string_filter(self, values_to_set, table_name, filter_string):
        con = sqlite3.connect(self.__path_to_db)

        query = "UPDATE {} SET ".format(table_name)
        for key in [*values_to_set]:
            tmp = self.__format_string_sql_friendly(values_to_set[key])
            query += "{} = {},".format(key, tmp)

        # get rid of the last comma
        query = query[:-1]
        query += "where {}".format(filter_string)

        with con:
            con.execute(query)

    def update_with_dict_filter(self, values_to_set, table_name, filter_dict, logic_and=True):
        if logic_and:
            logic = "AND"
        else:
            logic = "OR"

        filter_string = ""
        for key in [*filter_dict]:
            value_string = self.__format_string_sql_friendly(filter_dict[key])
            filter_string += "{} = {}".format(key, value_string)
            filter_string += logic + " "

        # get rid of the last OR or AND
        # if OR then the last space char also will be deleted
        filter_string = filter_string[:-(len(logic)+1)]
        self.update_with_string_filter(values_to_set, table_name, filter_string)

    def get_all_data_with_string_filter(self, table_name, columns="*", filter_string=""):
        con = sqlite3.connect(self.__path_to_db)

        if isinstance(columns, str):
            pass
        elif isinstance(columns, list) or isinstance(columns, set):
            tmp = ""
            for column in columns:
                tmp += "{}, ".format(column)
            columns = tmp[:-2]

        if filter_string != "":
            filter_string = "WHERE " + filter_string

        else:
            raise Exception("columns has to be string, list or set")

        with con:
            return con.execute("SELECT {} FROM {} {}".format(columns, table_name, filter_string)).fetchall()

    def get_all_data_with_dict_filter(self, table_name,  columns="*", filter_dict=None, logic_and=True):
        if logic_and:
            logic = "AND"
        else:
            logic = "OR"

        filter_string = ""
        if filter_dict is not None:
            for key in [*filter_dict]:
                value_string = self.__format_string_sql_friendly(filter_dict[key])
                filter_string += "{} = {} ".format(key, value_string)
                filter_string += logic + " "

        # get rid of the last OR or AND
        # if OR then the last space char also will be deleted
        filter_string = filter_string[:-(len(logic) + 1)]
        return self.get_all_data_with_string_filter(table_name, columns, filter_string)

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
                                nr = 1

                        else:
                            # if no auto create -> return -1
                            return -1

            if nr != 0:
                table_name = table_name + "_" + str(nr)
            return table_name

    def __format_string_sql_friendly(self, string_to_format):
        if type(string_to_format) is str:
            tmp = "%r" % string_to_format
            # in sqlite single quotes have to be replaced by double quotes
            tmp = tmp.replace(r"\'", r"''")
        else:
            tmp = "'" + str(string_to_format) + "'"
        return tmp

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
