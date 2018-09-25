from utils.data_file import DataFile
from utils.data_sql import DataSQL


class DataStorage(object):

    def __init__(self, hashtag, config):
        # initialize specific storage type
        if config.get('MAIN', 'store') == 'file':
            self.ptr = DataFile(hashtag)
        elif config.get('MAIN', 'store') == 'sql':
            self.ptr = DataSQL(hashtag)

    def save(self, data):
        self.ptr.save(data)

    def get_info(self):
        # get information were the data is saved
        return self.ptr.get_info()


