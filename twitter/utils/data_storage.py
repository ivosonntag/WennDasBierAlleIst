from utils.data_file import DataFile
from utils.data_sql import DataSQL


class DataStorage(object):

    def __init__(self, hashtag, type):
        # initialize specific storage type
        if type == 'file':
            self.ptr = DataFile(hashtag)
        elif type == 'sql':
            self.ptr = DataSQL(hashtag)

    def save(self, data):
        self.ptr.save(data)

    def get_info(self):
        # get information were the data is saved
        return self.ptr.get_info()


