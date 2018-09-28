import time
import os
from utils.data_storage import DataStorage


class DataFile(DataStorage):

    def __init__(self, hashtag, config):
        # in python calling base init method is optional
        self._set_data(hashtag, config)

        date_time = time.strftime("%Y-%m-%d")
        file_name = date_time + "_" + hashtag + ".json"
        dir_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/raw/")
        self.path_to_file = dir_name + file_name

    def save(self, data):
        with open(self.path_to_file, 'a') as f:
            f.write(str(data) + "\n")

    def get_info(self):
        return self.path_to_file
