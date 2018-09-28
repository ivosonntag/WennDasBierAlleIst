import logging
import os
import sqlite3
import datetime
import logging.config

from utils.log_conf import logging_dict

from tweepy import OAuthHandler
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger("helper")
analyser = SentimentIntensityAnalyzer()


def authenticate():
    # make sure to export your credentials with `source credentials`
    CONSUMER_KEY = os.getenv("CONSUMER_KEY")
    CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return auth


def determine_vader(text):
    vader = analyser.polarity_scores(text)
    compound = vader["compound"]
    return compound


def weighted(value):
    if value is None:
        return -float('inf')
    else:
        return value


def get_trends(api, where_on_earth_id=1, only_one=False):
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


def get_location_woeid(api, country_str=None, town_str=None):
    woeid = 1
    found = False
    if country_str:
        if len(country_str) == 2:
            country_str = country_str.upper()
        else:
            country_str = country_str.title()
        logger.debug("searching for country: {}".format(country_str))
    list_with_dicts_of_locations = api.trends_available()
    for location in list_with_dicts_of_locations:
        if location['country'] == country_str:
            woeid = location['woeid']
            found = True
        elif location['countryCode'] == country_str:
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


def create_db_connection(db_file):
    """ create a database connection to the SQLite database
            specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        logger.error("failed to establish connection to db: {}".format(db_file))
    return None


def get_time():
    now = datetime.datetime.now()
    return now


def build_logger(logger_name, logging_level):
    # configure logger
    logging.config.dictConfig(logging_dict(logging_level=logging_level))
    log = logging.getLogger(logger_name)
    return log
