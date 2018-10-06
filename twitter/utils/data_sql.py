from utils.data_storage import DataStorage
from utils.dict2sql import Dict2Sql


class DataSQL(DataStorage):
    """Implementation of abstract DataStorage Class
    """

    def __init__(self, config):
        self._set_data(config)
        # if database doesn't exist under this path it will be created automatically
        self.__path_to_file = self._path + "twitter.sqlite"
        self.__dict2sql = Dict2Sql(self.__path_to_file)

    def save(self, data, hashtag):
        self.__dict2sql.save(data, hashtag, True, True)

    def get_info(self):
        return self.__path_to_file





