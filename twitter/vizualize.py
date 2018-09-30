import pandas as pd
import configparser
import matplotlib.pyplot as plt

from utils.helper_functions import build_logger

file_to_vizualize = "2018-09-30_Messi.pkl"


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    path_to_data = config.get('MAIN', 'path_to_data')
    log_level = config.get('MAIN', 'log_level')

    logger = build_logger('streamer', log_level)

    df = pd.read_pickle(path_to_data + file_to_vizualize)
    logger.debug(list(df))
    # df.plot(x='created_at', y='sentiment', style='o')
    plt.scatter(df['created_at'], df['sentiment'], s=1, color='r')
    plt.show()
