import time
import datetime
import os
import configparser

import tweepy

from utils.dict2sql import Dict2Sql

from utils.helper_functions import authenticate,\
    create_db_connection,\
    get_time,\
    build_logger

from tweet_streamer import format_tweet_data


def get_tweet_ids_from_db(database):
    conn = create_db_connection(database)

    cur = conn.cursor()
    query = "SELECT id_str FROM All_Tweets where deleted = 'False' ORDER BY id_str"
    cur.execute(query)
    tweet_ids = cur.fetchall()

    list_of_ids = [i[0] for i in tweet_ids]
    return list_of_ids


def check_deletion(list_of_ids_to_check):
    try:
        list_of_all_online_tweets = api.statuses_lookup(list_of_ids_to_check)
        still_online_data = []
        offline_ids = []
        for tweet in list_of_all_online_tweets:
            formatted_online_data = format_tweet_data(tweet, tweet_attributes, user_attributes)
            formatted_online_data['last_seen'] = get_time()
            still_online_data.append(formatted_online_data)
        online_ids = [id_str['id_str'] for id_str in still_online_data]
        for each_id in list_of_ids_to_check:
            if each_id not in online_ids:
                offline_ids.append(each_id)
        return offline_ids, still_online_data
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
        one_tweet["last_seen"] = tweet[1]
        one_tweet["status"] = "online"
        tweets_id_date_list.append(one_tweet)
    return tweets_id_date_list


if __name__ == '__main__':
    # load config
    config = configparser.ConfigParser()
    config.read('config.ini')
    path_to_data = config.get('MAIN', 'path_to_data')
    db_name = config.get('SQL', 'db_name')
    batch_size = config.getint('DELETION', 'batch_size')
    log_level = config.get('MAIN', 'log_level')
    file_name = config.get('DELETION', 'file_name')
    interval = config.getint('DELETION', 'checking_interval')
    tweet_attributes = config.get("DELETION", "include_attributes").split(', ')
    user_attributes = config.get("DELETION", "user_attributes").split(', ')
    full_path_to_file = os.path.join(path_to_data, file_name)
    path_to_db = os.path.join(path_to_data, db_name)
    store_together = config.getboolean('MAIN', 'store_together')

    # build logger
    logger = build_logger("deletion-checker", log_level)

    # initiate Dict2Sql
    sql_db = Dict2Sql(path_to_db)

    while True:

        # authenticate with twitter api
        auth = authenticate()
        api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        # get 'tweet_id's and 'created_at' attribute
        logger.info("checking deleted tweets of: {}".format(path_to_db))

        # following line returns a huge list. Slice it for testing purpose
        # TODO: Go iteratively through sql db and not receive all at once
        all_tweet_ids = get_tweet_ids_from_db(path_to_db)  # [:1000]  # uncomment for slicing

        # following loop checks status of batches of 100 tweets
        remainder = True
        while remainder:
            logger.debug("number of remaining tweet to check: {}".format(len(all_tweet_ids)))

            # slice data into 2 lists: batch of 100 and remainder tweet ids
            batch, remainder = slice_data_into_batches(batch_size, all_tweet_ids)
            all_tweet_ids = remainder

            # offline_tweets is a list containing ONLY the tweets which are no longer online (=offline)
            offline_tweet_ids, still_online_tweets_data = check_deletion(batch)

            for online_tweet in still_online_tweets_data:
                sql_db.save(online_tweet, "checked_tweets", True, True)

            for offline_id in offline_tweet_ids:
                filter_dict = dict()
                set_values = dict()
                filter_dict['id_str'] = offline_id
                set_values['deleted'] = True
                logger.debug("setting deleted to True for id: {}".format(offline_id))
                sql_db.update_with_dict_filter(set_values, "All_Tweets", filter_dict)

            logger.debug("number of offline tweets found in this batch: {}".format(len(offline_tweet_ids)))
            logger.info("offline tweet ids: {}".format(offline_tweet_ids))

        logger.info("done checking status of tweets! - now waiting for next round...")
        logger.debug("--------------------------------------------------------------")
        while datetime.datetime.now().minute % interval != 0:
            # sleeping
            # print("sleeping")
            time.sleep(1)
