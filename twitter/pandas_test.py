import os
import pandas as pd

tweet_1 = {'created_at': 'Sun Sep 30 08:21:28 +0000 2018',
           'id_str': '1046314068578127873',
           'text': 'Wenn das die Gegner der #AfD sind, muß das aller Lebenserfahrung nach wohl eine ganz patente Partei sein, die vieles richtig macht. https://t.co/NNORuTaTdI',
           'name': 'Svenja',
           'screen_name': 'lara_svenja',
           'location': 'Berlin, Deutschland',
           'followers_count': 57,
           'friends_count': 160,
           'user_id_str': '2828176223',
           'place': None,
           'sentiment': -0.8316}
tweet_2 = {'created_at': 'Mon Sep 30 08:21:28 +0000 2018',
           'id_str': '1046314068572327873',
           'text': 'Wenn das die Gegner der #AfD sind, muß das aller Lebenserfahrung nach wohl eine ganz patente Partei sein, die vieles richtig macht. https://t.co/NNORuTaTdI',
           'name': 'Svenja',
           'screen_name': 'lara_svenja',
           'location': 'Berlin, Deutschland',
           'followers_count': 57,
           'friends_count': 160,
           'user_id_str': '2828176223',
           'place': None,
           'sentiment': -0.8316}

# s = pd.Series(tweet_1)
# df = pd.DataFrame([tweet_1])
# df = df.append([[tweet_1]])
# print(df)
# my_pickle = "my_pickle.pk"
# df.to_pickle(my_pickle)
# read_df = pd.read_pickle(my_pickle)
# print(read_df)
# df2 = pd.DataFrame([tweet_2])
# df = df.append(df2, ignore_index=True)
# print(len(df))
# result = pd.concat([dfT, df2T])
# print("result ", result)

df = pd.read_pickle(os.path.join(os.path.dirname(__file__), "data/raw/2018-09-30_Trump.pkl"))
print(df.describe())