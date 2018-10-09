import time
from utils.data_storage import DataStorage


class DataFile(DataStorage):
    def __init__(self, config):
        file_name = ""
        if config.getboolean('MAIN', 'store_together'):
            file_name = 'All_Tweets.json'
        super().__init__(config, file_name)

    def save(self, data, file_name):
        if not self._store_together:
            date_time = time.strftime("%Y-%m-%d")
            file_name = date_time + "_" + file_name + ".json"
            self._path_to_file = self._path + file_name
        with open(self._path_to_file, 'a') as f:
            f.write(str(data) + "\n")

    def get_info(self):
        if self._store_together:
            return self._path_to_file
        else:
            return "As json file in " + self._path

