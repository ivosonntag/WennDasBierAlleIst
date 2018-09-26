import abc

class DataStorage(object, metaclass=abc.ABCMeta):
    """Abstract Class for data storage.
       Do not create an object of this class!
    """
    @abc.abstractmethod
    def __init__(self):
        raise NotImplementedError('not defined')

    @abc.abstractmethod
    def save(self, data):
        # get information were the data is saved
        raise NotImplementedError('not defined')

    @abc.abstractmethod
    def get_info(self):
        # get information were the data is saved
        raise NotImplementedError('not defined')

    def _set_data(self, hashtag, config):
        self._hashtag = hashtag
        self._path = config.get('MAIN', 'path_to_data')
        self._list_of_keys = config.get('TWITTER', 'include_data').split(', ')
        del self._list_of_keys[self._list_of_keys.index('user')]
        temp = config.get('TWITTER', 'user_attributes').split(', ')
        temp = ['user_id_str' if x=='id_str' else x for x in temp]
        self._list_of_keys = sorted(self._list_of_keys + temp)

from utils.data_file import DataFile
from utils.data_sql import DataSQL

class StorageFactory(object):
    """ Factory Method Pattern
    """
    @staticmethod
    def create(hashtag, config):
        if config.get('MAIN', 'store') == 'file':
            return DataFile(hashtag, config)
        elif config.get('MAIN', 'store') == 'sql':
            return DataSQL(hashtag, config)



