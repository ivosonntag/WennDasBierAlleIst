import os
import configparser

import tweepy

from utils.helper_functions import authenticate,\
    create_db_connection,\
    get_time,\
    build_logger,\
    convert_twitter_time,\
    save_as_json_file, \
    load_json,\
    update_data_file


def get_tweet_ids_from_db(database):
    conn = create_db_connection(database)

    cur = conn.cursor()
    cur.execute("SELECT id_str, created_at FROM all_tweets where deleted = 'False' ORDER BY id_str")
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
    full_path_to_file = os.path.join(path_to_data, file_name)

    # build logger
    logger = build_logger("deletion-checker", log_level)

    # authenticate with twitter api
    auth = authenticate()
    api = tweepy.API(auth)

    # get 'tweet_id's and 'created_at' attribute
    path_to_db = os.path.join(path_to_data, db_name)
    # following line returns a huge list. Slice it for testing purpose
    # TODO: Go iteratively through sql db and not receive all at once
    all_tweet_ids_date = get_tweet_ids_from_db(path_to_db)  # [:10]  # uncomment for slicing

    # generate a list based on the info stored in the db, containing a dict per tweet,
    # dict contains tweet_id, last_seen (=date) and status (=online,offline)
    status_tweet_list = create_status_tweet_list(all_tweet_ids_date)

    # get only the ids of the
    all_ids = [i[0] for i in all_tweet_ids_date]

    # following loop checks status of batches of 100 tweets
    remainder = True
    while remainder:
        logger.info("number of remaining tweet to check: {}".format(len(all_ids)))

        # slice data into 2 lists: batch of 100 and remainder tweet ids
        batch, remainder = slice_data_into_batches(batch_size, all_ids)
        all_ids = remainder

        # offline_tweets is a list containing ONLY the tweets which are no longer online (=offline)
        offline_tweets = find_offline_ids(batch)

        logger.info("number of offline tweets found in this batch: {}".format(len(offline_tweets)))
        logger.debug("offline tweet ids: {}".format(offline_tweets))

        for tweet in status_tweet_list:
            for deleted_tweet_id in offline_tweets:
                if tweet["tweet_id"] == deleted_tweet_id:
                    tweet["status"] = "offline"
                else:
                    tweet["last_seen"] = get_time()
        # once remainder = 0 break loop

    logger.info("done checking status of tweets!")
    # if there is a data file already:
    if os.path.isfile(full_path_to_file):

        # load data file containing the described list with a dict per tweet (tweet_id, last_seen, status)
        logger.debug("loading {}".format(full_path_to_file))
        status_tweet_file = load_json(full_path_to_file)

        # update the loaded file, like:
        # if id is offline -> update status to offline
        # if id is still online -> update last_seen to recent date
        # if id is not in file already, add tweet dict to file
        logger.info("now updating data into {}".format(full_path_to_file))
        status_tweet_list = update_data_file(status_tweet_file, status_tweet_list)

    # in the end save the list with dicts to the loaded / new file
    logger.info("saving data to file: {}".format(full_path_to_file))
    save_as_json_file(full_path_to_file, status_tweet_list)
