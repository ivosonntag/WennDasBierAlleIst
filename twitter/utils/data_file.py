import time
from utils.data_storage import DataStorage


class DataFile(DataStorage):

    def __init__(self, config):
        # in python calling base init method is optional
        self._set_data(config)
        self.__path_to_file = ""

    def save(self, data, hashtag):
        date_time = time.strftime("%Y-%m-%d")
        file_name = date_time + "_" + hashtag + ".json"
        self.__path_to_file = self._path + file_name
        with open(self.__path_to_file, 'a') as f:
            f.write(str(data) + "\n")

    def get_info(self):
        return self.__path_to_file
