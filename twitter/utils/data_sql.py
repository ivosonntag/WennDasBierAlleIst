from utils.data_storage import DataStorage
from utils.dict2sql import Dict2Sql


class DataSQL(DataStorage):
    """Implementation of abstract DataStorage Class
    """

    def __init__(self, config):
        super().__init__(config, config.get('SQL', 'db_name'))
        self.__dict2sql = Dict2Sql(self._path_to_file)
        self.__table_name = ""
        if self._store_together:
            self.__table_name = "All_Tweets"

    def save(self, data, table_name):
        if not self._store_together:
            self.__table_name = table_name

        data['deleted'] = False
        self.__dict2sql.save(data, self.__table_name, True, True)

    def get_info(self):
        tmp_str = "Database: " + self._path_to_file
        if self.__table_name is not "":
            tmp_str += " | Table: " + self.__table_name
        return tmp_str





