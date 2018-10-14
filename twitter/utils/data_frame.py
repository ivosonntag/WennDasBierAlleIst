import time
import os
import logging

import pandas as pd

from utils.data_storage import DataStorage


logger = logging.getLogger("data-frame")


class DataFrame(DataStorage):

    def __init__(self, config):
        file_name = ""
        if config.getboolean('MAIN', 'store_together'):
            file_name = 'All_Tweets.json'
        super().__init__(config, file_name)
        # in python calling base init method is optional
        # self._set_data(config)
        self._df_fom_file = None
        self._batch_df = None
        self.path_to_file = None
        self.buffer_size = config.getint('MAIN', 'df_buffer_size')

    def save(self, data, hashtag):
        date_time = time.strftime("%Y-%m-%d")
        file_name = date_time + "_" + hashtag + ".pkl"
        dir_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), self._path)
        self.path_to_file = dir_name + file_name
        # create data frame form tweet data dict

        temp_df = pd.DataFrame([data])
        # check if there is a batch data frame already
        if self._batch_df is None:
            # if not create a new batch data frame
            self._batch_df = temp_df
        else:
            # if there is a batch data frame, concatenate recent temporary data frame
            self._batch_df = pd.concat([self._batch_df, temp_df], ignore_index=True)
        logger.debug("batch data frame: {}\n".format(self._batch_df))
        # if length of batch data frame reaches the buffer limit, concatenate data to pickle file
        if len(self._batch_df) == self.buffer_size:
            logger.info("data frame buffer reached limit of {}, saving data to pickle file".format(self.buffer_size))
            if os.path.isfile(self.path_to_file):
                logger.debug("found pickle file, loading...")
                self._df_fom_file = pd.read_pickle(self.path_to_file)
                logger.debug("merging file df with batch df")
                pd.to_pickle(pd.concat([self._df_fom_file, self._batch_df]), self.path_to_file)
            else:
                pd.to_pickle(self._batch_df, self.path_to_file)
            self._batch_df = temp_df = None

    def get_info(self):
        return self.path_to_file
