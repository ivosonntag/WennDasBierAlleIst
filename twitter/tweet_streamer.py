from utils.log_conf import logging_dict
from utils.data_storage import DataStorage
import logging.config

from tweepy import Stream
from tweepy.streaming import StreamListener
import tweepy
from tweepy import OAuthHandler
import textblob
import json
import os
import time

hashtag = 'Messi'

# configure logger
logging.config.dictConfig(logging_dict(logger_name="tvizzer", logging_level='DEBUG'))
logger = logging.getLogger("tvizzer")
log = True

# make sure to export your credentials with `source credentials`
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")


def format_tweet_data(tweet, plot=False):
    data = json.loads(tweet)
    # logger.debug("data: {} ".format(data))

    # added to get the full text if status exceeds 140 characters
    if "extended_tweet" in data:
        text = data['extended_tweet']['full_text']
    else:
        text = data["text"]

    blob = textblob.TextBlob(text)
    sentiment = round(blob.sentiment.polarity, 2)

    # see https://github.com/ivosonntag/WennDasBierAlleIst/wiki/twitter for different keys
    tweet_info = {"tweet_id" : data["id_str"],
                  "user_id": data["user"]["id_str"],
                  "hashtag": hashtag,
                  "time": time.strftime("%Y-%m-%d_%H:%M:%S"),
                  "language": data["lang"],
                  "sentiment": sentiment,
                  "text": text}

    # return data
    return tweet_info


def get_trends():
    trends1 = api.trends_place(1)
    data = trends1[0]
    trends = data["trends"]
    names = [trend['name'] for trend in trends]
    return names


class MyListener(StreamListener):

    def on_data(self, data):
        # only gets called if new status was posted
        # see StreamListener class for different events
        try:
            tweet_info = format_tweet_data(data, plot=False)
            if log: logger.debug(tweet_info)
            storage.save(tweet_info)

        except BaseException as e:
            logger.error("Error on_data: {}".format(str(e)), exc_info=True)
        return True

    def on_error(self, status):
        logger.warning(status)
        return True


if __name__ == '__main__':
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    storage = DataStorage(hashtag, 'file')

    api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    # logger.info("rate limit status: {}".format(api.rate_limit_status()))

    logger.info("current trends: {}".format(get_trends()))
    logger.info("saving data with hashtag '{}' to: '{}'".format(hashtag, storage.get_info()))

    twitter_stream = Stream(auth, MyListener())
    try:
        twitter_stream.filter(track=[hashtag], languages=["en"])
    except ValueError as e:
        logger.error("failed to access twitter authentication - make sure to export credentials to environment, with "
                     "exception {}".format(e), exc_info=True)

    api = tweepy.API(auth)
