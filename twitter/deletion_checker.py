import os
import configparser

import tweepy

from utils.helper_functions import authenticate, create_db_connection, get_time, build_logger


# last entry in this list of 3 ids is offline
list_of_example_ids = [1045396895559020545, 1045396901397516293, 1014681067851128833]


def get_tweet_ids(database):
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


def process_batch_limitation(batch_limitation, full_data):
    pass


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    path_to_data = config.get('MAIN', 'path_to_data')
    db_name = config.get('MAIN', 'db_name')
    log_level = config.get('MAIN', 'log_level')

    logger = build_logger("deletion-checker", log_level)

    auth = authenticate()
    api = tweepy.API(auth)

    path_to_db = os.path.join(path_to_data, db_name)
    all_tweet_ids = get_tweet_ids(path_to_db)[:100]       # pick just a few for testing

    logger.debug("list of ids: {}".format(all_tweet_ids))
    logger.debug("len of list of tweet ids to check: {}".format(len(all_tweet_ids)))

    offline_tweets = find_offline_ids(all_tweet_ids)
    logger.debug("number of offline tweets: {}".format(len(offline_tweets)))
    logger.debug("offline tweets: {}".format(offline_tweets))


