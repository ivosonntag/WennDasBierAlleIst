import sqlite3
import os
import time


class DataSQL(object):
    def __init__(self, hashtag):
        # if database doesn't exist under this path it will be created
        dir_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/raw/")
        file_name = 'twitter.sqlite'
        self.path_to_file = dir_name + file_name
        self.hashtag = hashtag
        conn = sqlite3.connect(self.path_to_file)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # create table if it doesnt exists
        query = "create table if not exists {} ("\
            "'ID' TEXT NOT NULL,"\
            "'Text' TEXT,"\
            "'Sentiment' REAL,"\
            "'DateTime' TEXT,"\
            "PRIMARY KEY('ID')"\
            ");".format(hashtag)
        c.execute(query)
        conn.close()

    def save(self, data):
        conn = sqlite3.connect(self.path_to_file)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        raw_text = "%r"% data['text']
        query = "insert into {} (ID, Text, Sentiment, DateTime)" \
                "values ({}, {}, {}, {})".format(self.hashtag, data['tweet_id'],
                raw_text, data['sentiment'], "%r"%(time.strftime("%Y-%m-%d_%H:%M:%S")))
        c.execute(query)
        conn.commit()
        conn.close()

    def get_info(self):
        return self.path_to_file