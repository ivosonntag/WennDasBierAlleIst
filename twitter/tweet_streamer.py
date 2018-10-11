import configparser
from urllib3.exceptions import ProtocolError, ReadTimeoutError

import tweepy
from tweepy.streaming import StreamListener
from tweepy import Stream

from utils.data_storage import StorageFactory
from utils.helper_functions import authenticate,\
    determine_vader,\
    get_trends,\
    get_location_woeid,\
    build_logger,\
    convert_twitter_time


global logger, config


def format_tweet_data(tweet, attributes_to_include, user_attributes_to_include):
    sentiment = None
    data = tweet._json
    # added to get the full text if status exceeds 140 characters
    if "extended_tweet" in data:
        text = data['extended_tweet']['full_text']
    elif 'retweeted_status' in data and "extended_tweet" in data['retweeted_status']:
        text = data['retweeted_status']['extended_tweet']['full_text']
    else:
        text = data["text"]
    if "sentiment" in attributes_to_include:
        sentiment = determine_vader(text)
    # see https://github.com/ivosonntag/WennDasBierAlleIst/wiki/twitter for different keys
    tweet_info = dict()
    for attribute in attributes_to_include:
        if attribute == 'user':
            user = dict()
            for user_attribute in user_attributes_to_include:
                # if user_attribute == 'id_str':
                #    user['user_id_str'] = data['user'][user_attribute]
                # else:
                user[user_attribute] = data['user'][user_attribute]
            tweet_info['user'] = user
            # merge two dicts
            # tweet_info = {**tweet_info, **user}
        elif attribute == 'text':
            tweet_info[attribute] = text
        elif attribute == 'place':
            tweet_info[attribute] = data[attribute]
            if tweet_info[attribute] is not None and 'full_name' in tweet_info[attribute]:
                tweet_info[attribute] = data[attribute]['full_name']
        elif attribute == 'created_at':
            tweet_info[attribute] = convert_twitter_time(data[attribute])
        elif attribute == 'sentiment':
            tweet_info[attribute] = sentiment
        else:
            tweet_info[attribute] = data[attribute]
    return tweet_info


def get_hashtag_of_tweet(tweet_info):
    # since there is no function in MyListener for getting which hashtag triggered
    # the callback function, we have to look for it manually, therefore we count the occurrences
    # of the hashtags in the tweet text
    if len(storage) == 1:
        return list(storage.keys())[0]

    cnt = 0
    ht_max = ""
    for ht in storage.keys():
        tmp = count_substr_in_str(ht, tweet_info['text'])
        if tmp > cnt:
            ht_max = ht
            cnt = tmp

    if cnt == 0:
        return -1
    return ht_max


def count_substr_in_str(substr, theStr):
    num = i = 0
    while True:
        j = theStr.lower().find(substr.lower(), i)
        if j == -1:
            break
        num += 1
        i = j + 1
    return num


class MyListener(StreamListener):

    def on_status(self, status):
        # only gets called if new status was posted
        # see StreamListener class for different events
        try:
            tweet_info = format_tweet_data(status, tweet_attributes, user_attributes)
            hashtag = get_hashtag_of_tweet(tweet_info)
            if hashtag != -1:
                if console_output:
                    logger.info(tweet_info)
                storage[hashtag].save(tweet_info, hashtag)
            else:
                # for example if the retweetet tweet contained the hashtag or if the hashtag is in the user info
                if console_output:
                    logger.debug('Tweet without hashtag.')

        except Exception as e:
            logger.error("Error on_data: {}".format(str(e)), exc_info=True)
        return True

    def on_error(self, status):
        logger.warning("Error: ".format(status))
        return True


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    # get config data
    console_output = config.getboolean('MAIN', 'print_to_console')
    hashtags = config.get('TWITTER', 'hashtag')
    hashtags_list = config.get('TWITTER', 'hashtag').split(', ')
    country = config.get('TWITTER', 'country')
    town = config.get('TWITTER', 'town')
    language = config.get('TWITTER', 'language')
    tweet_attributes = config.get("TWITTER", "include_attributes").split(', ')
    user_attributes = config.get("TWITTER", "user_attributes").split(', ')
    log_level = config.get('MAIN', 'log_level')

    logger = build_logger('streamer', log_level)

    logger.debug("include attributes: {}".format(tweet_attributes))
    logger.debug("user_attribute: {}".format(user_attributes))

    auth = authenticate()
    api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    if config.getboolean('TWITTER', 'use_most_trending'):
        hashtags = get_trends(api, get_location_woeid(api, country, town), only_one=True)

    storage = {}
    for hashtag in hashtags_list:
        storage[hashtag] = StorageFactory.create(config)
        logger.info("saving data with hashtag '{}' to: '{}'".format(hashtag, storage[hashtag].get_info()))

    twitter_stream = Stream(auth, MyListener())
    try:
        twitter_stream.filter(track=[hashtags], languages=[language])
    except ValueError as e:
        logger.error("failed to access twitter authentication - make sure to export credentials to environment, with "
                     "exception {}".format(e))
    except ProtocolError and ReadTimeoutError as e:
        logger.error("Connection broken: {}".format(e), exc_info=True)
