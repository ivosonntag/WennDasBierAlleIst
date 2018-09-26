from utils.data_storage import StorageFactory
import logging.config

import json
import os
import configparser
import textblob

import tweepy
from tweepy.streaming import StreamListener
from tweepy import Stream
from tweepy import OAuthHandler

from utils.log_conf import logging_dict
import logging.config


global logger, config

config = configparser.ConfigParser()
config.read('config.ini')


def weighted(value):
    if value is None:
        return -float('inf')
    else:
        return value


def format_tweet_data(tweet):
    sentiment = None
    data = json.loads(tweet)
    # added to get the full text if status exceeds 140 characters
    if "extended_tweet" in data:
        text = data['extended_tweet']['full_text']
    else:
        text = data["text"]
    if config.getboolean('MAIN', 'sentiment'):
        sentiment = determine_sentiment(text)
    # see https://github.com/ivosonntag/WennDasBierAlleIst/wiki/twitter for different keys
    desired_attributes = config.get('TWITTER', 'include_data').split(', ')
    user_attributes = config.get('TWITTER', 'user_attributes').split(', ')
    tweet_info = dict()
    for attribute in desired_attributes:
        if attribute == 'user':
            user = dict()
            for user_attribute in user_attributes:
                if user_attribute == 'id_str':
                    user['user_id_str'] = data['user'][user_attribute]
                else:
                    user[user_attribute] = data['user'][user_attribute]
            # tweet_info['user'] = user
            # merge two dicts
            tweet_info = {**tweet_info, **user}
        elif attribute == 'text':
            tweet_info[attribute] = text
        elif attribute == 'sentiment':
            tweet_info[attribute] = sentiment
        else:
            tweet_info[attribute] = data[attribute]
    return tweet_info


def determine_sentiment(text):
    blob = textblob.TextBlob(text)
    sentiment = round(blob.sentiment.polarity, 3)
    return sentiment


def get_trends(where_on_earth_id=1, only_one=False):
    logger.debug("getting trends for woeid: {}".format(where_on_earth_id))
    trends = api.trends_place(where_on_earth_id)[0]
    trends = trends["trends"]
    all_hashtags = list()
    for trend in trends:
        tweet = dict()
        tweet['tweet'] = trend['name']
        tweet['tweet_volume'] = trend['tweet_volume']
        all_hashtags.append(tweet)
    sorted_hashtags = sorted(all_hashtags, key=lambda k: weighted(k['tweet_volume']), reverse=True)
    if only_one:
        hashtag = sorted_hashtags[0]["tweet"]
    else:
        hashtag = sorted_hashtags
    return hashtag


def get_location_woeid(country_str=None, town_str=None):
    woeid = 1
    found = False
    if country_str:
        if len(country_str) == 2:
            country_str = country_str.upper()
        else:
            country_str = country_str.title()
    list_with_dicts_of_locations = api.trends_available()
    for location in list_with_dicts_of_locations:
        if location['country'] == country_str:
            woeid = location['woeid']
            found = True
        elif location['countryCode'] == country:
            woeid = location['woeid']
            found = True
        elif location['name'] == town_str:
            woeid = location['woeid']
            found = True
    if found:
        return woeid
    else:
        logger.error("Could not find provided country or town, try the '-w' argument."
                     "Will continue with woeid=1 which means global")
        return woeid


def filter_data(tweet, include_data, user_attributes):
    filtered_data = dict()
    for attribute in include_data:
        if attribute == 'user':

            user = dict()
            for user_attribute in user_attributes:
                user[user_attribute] = tweet['user'][user_attribute]
            filtered_data['user'] = user
        else:
            filtered_data[attribute] = tweet[attribute]
    return filtered_data


class MyListener(StreamListener):

    def on_data(self, data):
        # only gets called if new status was posted
        # see StreamListener class for different events
        try:
            tweet_info = format_tweet_data(data)
            if console_output:
                logger.debug(tweet_info)
            storage.save(tweet_info)

        except BaseException as e:
            logger.error("Error on_data: {}".format(str(e)), exc_info=True)
        return True

    def on_error(self, status):
        logger.warning(status)
        return True


if __name__ == '__main__':
    console_output = config.get('MAIN', 'print_to_console')

    hashtag = config.get('TWITTER', 'hashtag')
    country = config.get('TWITTER', 'country')
    town = config.get('TWITTER', 'town')
    store = config.get('MAIN', 'store')

    # configure logger
    logging.config.dictConfig(logging_dict(logger_name="tvizzer", logging_level=config.get('MAIN', 'log_level')))
    logger = logging.getLogger("tvizzer")

    tweet_data = config.get("TWITTER", "include_data").split(', ')
    logger.debug("include data: {}".format(tweet_data))
    user_data = config.get("TWITTER", "user_attributes").split(', ')
    logger.debug("user_attribute: {}".format(user_data))

    # make sure to export your credentials with `source credentials`
    CONSUMER_KEY = os.getenv("CONSUMER_KEY")
    CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    if config.getboolean('TWITTER', 'use_most_trending'):
        hashtag = get_trends(get_location_woeid(country, town), only_one=True)

    storage = StorageFactory.create(hashtag, config)

    logger.info("saving data with hashtag '{}' to: '{}'".format(hashtag, storage.get_info()))

    twitter_stream = Stream(auth, MyListener())
    try:
        twitter_stream.filter(track=[hashtag], languages=["en"])
    except ValueError as e:
        logger.error("failed to access twitter authentication - make sure to export credentials to environment, with "
                     "exception {}".format(e), exc_info=True)
