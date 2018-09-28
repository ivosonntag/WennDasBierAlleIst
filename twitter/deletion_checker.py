import os
import time
import configparser

import tweepy

from utils.helper_functions import authenticate, create_db_connection, get_time, build_logger


# last entry in this list of 3 ids is offline
list_of_example_ids = [1045396895559020545, 1045396901397516293, 1014681067851128833]


def get_tweet_ids_from_db(database):
    conn = create_db_connection(database)

    cur = conn.cursor()
    cur.execute("SELECT id_str FROM AFD_0 ORDER BY id_str")
    tweet_ids = cur.fetchall()

    list_of_ids = [int(i[0]) for i in tweet_ids]
    return list_of_ids


def find_offline_ids(list_of_ids_to_check):
    try:
        list_of_all_online_tweets = api.statuses_lookup(list_of_ids_to_check)
        still_online_ids = []
        for tweet in list_of_all_online_tweets:
            online_id = tweet._json['id']
            still_online_ids.append(online_id)
        offline_ids = []
        for each_id in list_of_ids_to_check:
            if each_id not in still_online_ids:
                offline_ids.append(each_id)
        return offline_ids
    except Exception as e:
        logger.error("got Exception while statuses_lookup: {}".format(e), exc_info=True)
        return None


def slice_data_into_batches(batch_limitation, full_data):
    sliced_batch = full_data[:batch_limitation]
    remainder_batch = full_data[batch_limitation:]
    return sliced_batch, remainder_batch


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    path_to_data = config.get('MAIN', 'path_to_data')
    db_name = config.get('MAIN', 'db_name')
    batch_size = config.getint('DELETION', 'batch_size')
    log_level = config.get('MAIN', 'log_level')

    logger = build_logger("deletion-checker", log_level)

    auth = authenticate()
    api = tweepy.API(auth)

    path_to_db = os.path.join(path_to_data, db_name)
    # pick just a few for testing
    all_tweet_ids = get_tweet_ids_from_db(path_to_db)   # returns a huge list of all tweet ids

    # logger.debug("list of ids: {}".format(all_tweet_ids))

    while True:
        logger.debug("number of tweet ids to check: {}".format(len(all_tweet_ids)))

        batch, remainder = slice_data_into_batches(batch_size, all_tweet_ids)
        all_tweet_ids = remainder

        offline_tweets = find_offline_ids(batch)

        logger.debug("number of offline tweets: {}".format(len(offline_tweets)))
        logger.info("offline tweet ids: {}".format(offline_tweets))

