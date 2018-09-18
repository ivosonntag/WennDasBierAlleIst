from utils.log_conf import logging_dict
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

# make sure to export your credentials with `source credentials`
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")


def data_file(tag):
    date_time = time.strftime("%Y-%m-%d")
    file_name = date_time + "_" + tag + ".json"
    dir_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/raw/")
    path_to_file = dir_name + file_name
    return path_to_file


def determine_sentiment(tweet, plot=False):
    data = json.loads(tweet)
    # logger.debug("data: {} ".format(data))
    text = data["text"]
    blob = textblob.TextBlob(text)
    sentiment = round(blob.sentiment.polarity, 2)
    tweet_info = {"hashtag": hashtag,
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
        try:
            with open(data_file(hashtag), 'a') as f:
                tweet_info = determine_sentiment(data, plot=False)
                logger.debug(tweet_info)
                f.write(str(tweet_info) + "\n")
                # time.sleep(1)
                return True
        except BaseException as e:
            logger.error("Error on_data: {}".format(str(e)), exc_info=True)
        return True

    def on_error(self, status):
        logger.warning(status)
        return True


if __name__ == '__main__':
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    # logger.info("rate limit status: {}".format(api.rate_limit_status()))

    logger.info("current trends: {}".format(get_trends()))
    logger.info("saving data with hashtag '{}' to file: '{}'".format(hashtag, data_file(hashtag)))

    twitter_stream = Stream(auth, MyListener())
    try:
        twitter_stream.filter(track=[hashtag], languages=["en"])
    except ValueError as e:
        logger.error("failed to access twitter authentication - make sure to export credentials to environment, with "
                     "exception {}".format(e), exc_info=True)

    api = tweepy.API(auth)
