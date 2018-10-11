import pandas as pd
import sqlite3

file_to_load = "data/processed/deleted_tweets.json"
save_to_file = "data/processed/offline_tweets.txt"

if __name__ == '__main__':

    df = pd.read_json(file_to_load)
    deleted_id_list = df[df['status'] == "offline"]["tweet_id"]
    # print(len(df))
    con = sqlite3.connect("data/raw/twitter.sqlite.dl")
    with con:
        for deleted_id in deleted_id_list:
            tweet_text = con.execute("select text from AFD_0 where id_str = {}".format(deleted_id)).fetchall()
            with open(save_to_file, "a") as myfile:
                # print(str(tweet_text))
                myfile.write(str(tweet_text))
