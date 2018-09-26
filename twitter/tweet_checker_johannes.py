from random import randint
import os
import tweepy
from tweepy import OAuthHandler


# make sure to export your credentials with `source credentials`
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")


def check_tweet_status(tweet_id):
    #checks if a tweet with tweet_id is still online
    tweet_status = api.get_status(1044681067851128833)
    if tweet_status:
        return 1
    else:
        return 0


if __name__ == '__main__':
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    #check 101 random ids and print text if tweet is still online
    for i in range(0, 100):
        random_tweet_id = randint(1014681067851128833, 1024681067851148833)
        online_status = check_tweet_status(1014681067851128833)
        print(online_status)
        if online_status == 1:
            tweet_online = api.statuses_lookup([random_tweet_id])
            print(tweet_online[0].text)

