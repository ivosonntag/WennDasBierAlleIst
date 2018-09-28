import os
import configparser

import tweepy

from utils.helper_functions import authenticate,\
    create_db_connection,\
    get_time,\
    build_logger,\
    convert_twitter_time,\
    save_as_json_file, \
    load_json


def get_tweet_ids_from_db(database):
    conn = create_db_connection(database)

    cur = conn.cursor()
    cur.execute("SELECT id_str, created_at FROM AFD_0 ORDER BY id_str")
    tweet_ids = cur.fetchall()

    list_of_ids = [i for i in tweet_ids]
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
            if int(each_id) not in still_online_ids:
                offline_ids.append(each_id)
        return offline_ids
    except Exception as e:
        logger.error("got Exception while statuses_lookup: {}".format(e), exc_info=True)
        return None


def slice_data_into_batches(batch_limitation, full_data):
    sliced_batch = full_data[:batch_limitation]
    remainder_batch = full_data[batch_limitation:]
    return sliced_batch, remainder_batch


def create_status_tweet_list(data):
    tweets_id_date_list = []
    for tweet in data:
        one_tweet = dict()
        one_tweet["tweet_id"] = tweet[0]
        one_tweet["last_seen"] = convert_twitter_time(tweet[1])
        one_tweet["status"] = "online"
        tweets_id_date_list.append(one_tweet)
    return tweets_id_date_list


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    path_to_data = config.get('MAIN', 'path_to_data')
    db_name = config.get('MAIN', 'db_name')
    batch_size = config.getint('DELETION', 'batch_size')
    log_level = config.get('MAIN', 'log_level')
    file_name = config.get('DELETION', 'file_name')
    full_path_to_file = os.path.join(path_to_data, file_name)

    logger = build_logger("deletion-checker", log_level)

    auth = authenticate()
    api = tweepy.API(auth)

    path_to_db = os.path.join(path_to_data, db_name)
    # pick just a few for testing
    all_tweet_ids_date = get_tweet_ids_from_db(path_to_db)[:200]   # returns a huge list of all tweet ids

    if os.path.isfile(full_path_to_file):
        logger.info("loading {}".format(full_path_to_file))
        status_tweet_list = load_json(full_path_to_file)
    else:
        logger.error("no file found, creating new one".format(full_path_to_file))
        status_tweet_list = create_status_tweet_list(all_tweet_ids_date)
    # logger.debug(status_tweet_list)

    all_ids = [i[0] for i in all_tweet_ids_date]
    # logger.debug("all ids from database: {}".format(all_ids))

    remainder = True
    while remainder:
        logger.debug("number of tweet ids to check: {}".format(len(all_ids)))

        batch, remainder = slice_data_into_batches(batch_size, all_ids)
        all_ids = remainder

        # logger.info("batch: {}".format(batch))
        # logger.info("remainder: {}".format(remainder))
        offline_tweets = find_offline_ids(batch)

        logger.debug("number of offline tweets: {}".format(len(offline_tweets)))
        logger.info("offline tweet ids: {}".format(offline_tweets))
        # time.sleep(1)
        for tweet in status_tweet_list:
            for deleted_tweet in offline_tweets:
                if tweet["tweet_id"] == deleted_tweet:
                    tweet["status"] = "offline"
                else:
                    tweet["last_seen"] = get_time()

    # logger.info("your list: {}".format(status_tweet_list))
    save_as_json_file(full_path_to_file, status_tweet_list)
    logger.debug("done checking status of tweets!")
