import sqlite3

import tweepy
from tweepy.error import TweepError

from utils.helper_functions import authenticate

# list of ids
example_ids = {
    1044681067851128833: "online",
    1014681067851128833: "offline"
}


def check_tweet_status(tweet_id):
    try:
        api.get_status(1014681067851128833)
    except TweepError:
        return 0
    else:
        return 1


if __name__ == '__main__':
    auth = authenticate()
    api = tweepy.API(auth)

    online_status = check_tweet_status(1014681067851128833)
    if online_status == 1:
        print("online")
    else:
        print("offline")
