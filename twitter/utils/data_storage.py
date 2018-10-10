import abc


class DataStorage(object, metaclass=abc.ABCMeta):
    """Abstract Class for data storage.
       Do not create an object of this class!
    """
    @abc.abstractmethod
    def __init__(self, config, filename):
        self._path = config.get('MAIN', 'path_to_data')
        self._path_to_file = self._path + filename
        self._store_together = config.getboolean('MAIN', 'store_together')

    @abc.abstractmethod
    def save(self, data, hashtag):
        # save data
        raise NotImplementedError('not defined')

    @abc.abstractmethod
    def get_info(self):
        # get information were the data is saved
        raise NotImplementedError('not defined')


from utils.data_file import DataFile
from utils.data_sql import DataSQL
from utils.data_frame import DataFrame


class StorageFactory(object):
    """ Factory Method Pattern
    """
    @staticmethod
    def create(config):
        if config.get('MAIN', 'store_type') == 'file':
            return DataFile(config)
        elif config.get('MAIN', 'store_type') == 'sql':
            return DataSQL(config)
        elif config.get('MAIN', 'store_type') == 'pandas':
            return DataFrame(config)




