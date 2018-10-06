import abc


class DataStorage(object, metaclass=abc.ABCMeta):
    """Abstract Class for data storage.
       Do not create an object of this class!
    """
    @abc.abstractmethod
    def __init__(self):
        raise NotImplementedError('not defined')

    @abc.abstractmethod
    def save(self, data, hashtag):
        # get information were the data is saved
        raise NotImplementedError('not defined')

    @abc.abstractmethod
    def get_info(self):
        # get information were the data is saved
        raise NotImplementedError('not defined')

    def _set_data(self, config):
        self._path = config.get('MAIN', 'path_to_data')


from utils.data_file import DataFile
from utils.data_sql import DataSQL
from utils.data_frame import DataFrame


class StorageFactory(object):
    """ Factory Method Pattern
    """
    @staticmethod
    def create(config):
        if config.get('MAIN', 'store') == 'file':
            return DataFile(config)
        elif config.get('MAIN', 'store') == 'sql':
            return DataSQL(config)
        elif config.get('MAIN', 'store') == 'pandas':
            return DataFrame(config)




