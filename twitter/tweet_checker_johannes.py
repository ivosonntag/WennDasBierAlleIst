from utils.log_conf import logging_dict
import logging.config

from tweepy import Stream
from tweepy.streaming import StreamListener
from tweepy.parsers import JSONParser
import tweepy
from tweepy import OAuthHandler
import textblob
import json
import os
import time

CONSUMER_KEY="TWtqLUtoPwVXU0MQ5ePj2pZvT"
CONSUMER_SECRET="noodzTUVc8VEpUFEZo4RgwL7abpdMpRVo9QhgXqTgixWeSQJU2"
ACCESS_TOKEN="3581285302-j0r6tCTdO8Kfz8669nw8qCy0kLj4YApokRgp2RQ"
ACCESS_TOKEN_SECRET="kBA1Bh3Hcithn3EB8T8CnosyucqGOsv48Ugpas4t6WePH"

hashtag = "#"

# configure logger
logging.config.dictConfig(logging_dict(logger_name="tvizzer", logging_level='DEBUG'))
logger = logging.getLogger("tvizzer")

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

#override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

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

def data_file(tag):
    date_time = time.strftime("%Y-%m-%d")
    file_name = date_time + "_" + tag + ".json"
    dir_name = os.path.join(os.path.dirname(__file__), "data/raw/")
    path_to_file = dir_name + file_name

    return path_to_file


if __name__ == '__main__':
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    #api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    # logger.info("rate limit status: {}".format(api.rate_limit_status()))



    api = tweepy.API(auth)
    tweet_online = api.statuses_lookup([100])
    for tweet in tweet_online:
        print(str(tweet['text']))
    #myStreamListener = MyStreamListener()
    #myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener())
    #myStream.filter(track=['python'])

    #timeline = api.user_timeline(screen_name='jknabbe')
    #data = json.dumps(timeline)
    #print(data)


    #data = json.loads(tweet_online)
    #text = data["text"]
    #print(text)
        #public_tweets = api.home_timeline()
    #for tweet in public_tweets:
    #    print(tweet.text)


    #logger.info("current trends: {}".format(get_trends()))
    #logger.info("saving data with hashtag '{}' to file: '{}'".format(hashtag, data_file(hashtag)))

    #twitter_stream = Stream(auth, MyListener())
    #try:
    #    twitter_stream.filter(track=[hashtag], languages=["en"])
    #except ValueError as e:
    #    logger.error("failed to access twitter authentication - make sure to export credentials to environment, with "
    #                 "exception {}".format(e), exc_info=True)

    #api = tweepy.API(auth)