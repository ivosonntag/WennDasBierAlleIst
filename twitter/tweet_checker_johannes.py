from random import randint
import tweepy
from tweepy import OAuthHandler


CONSUMER_KEY="TWtqLUtoPwVXU0MQ5ePj2pZvT"
CONSUMER_SECRET="noodzTUVc8VEpUFEZo4RgwL7abpdMpRVo9QhgXqTgixWeSQJU2"
ACCESS_TOKEN="3581285302-j0r6tCTdO8Kfz8669nw8qCy0kLj4YApokRgp2RQ"
ACCESS_TOKEN_SECRET="kBA1Bh3Hcithn3EB8T8CnosyucqGOsv48Ugpas4t6WePH"


def check_tweet_status(tweet_id):
    #checks if a tweet with tweet_id is still online
    tweet_status = api.statuses_lookup([tweet_id])
    if tweet_status:
        return 1
    else:
        return 0

if __name__ == '__main__':
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)


    api = tweepy.API(auth)
    #check 101 random ids and print text if tweet is still online
    for i in range(0,100):
        random_tweet_id = randint(1000,10000000)
        online_status = check_tweet_status(random_tweet_id)
        print(online_status)
        if online_status == 1:
            tweet_online = api.statuses_lookup([random_tweet_id])
            print(tweet_online[0].text)

