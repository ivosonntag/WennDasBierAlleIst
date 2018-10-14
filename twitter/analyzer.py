import os
from collections import Counter

import configparser
from nltk import pos_tag
from nltk.tokenize import TweetTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import matplotlib.pyplot as plt

from utils.helper_functions import build_logger, get_time
from utils.dict2sql import Dict2Sql

global config
config = configparser.ConfigParser()
config.read('config.ini')


class Analyzer(object):
    def __init__(self, data=config.get('SQL', 'db_name')):
        self.file_name = data
        self.path_to_data = config.get('MAIN', 'path_to_data')
        self.path_to_plots = config.get('MAIN', 'path_to_plots')
        self.path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), self.path_to_data), data)
        self.table_name = config.get('SQL', 'default_table')
        self.hashtags_list = config.get('TWITTER', 'hashtag').split(', ')
        self.special_characters = ['!', ':', ',', '?', '.', ';', '´', '`', '´´', '``', '"', "'", '”', '(', ')', '–',
                                   '—', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                                   'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'rt', '’', '‘', '“', '-', '*', '&', '/',
                                   '#', '%', '\\', '\\\\', '...', '+', '„', '➡', ':/', 'au', 'al', 'ab', 'un', 'be',
                                   'wa', 'de', 'bi']
        log_level = config.get('MAIN', 'log_level')
        global logger
        logger = build_logger('analyzer', log_level)
        logger.info("analyzing file: {}".format(self.path))

    def get_sql_data(self, table_name=False, columns="*", filter_string=""):
        sql_db = Dict2Sql(self.path)
        if table_name:
            self.table_name = table_name
        data_frame = sql_db.get_all_data_with_string_filter(self.table_name, columns, filter_string, as_data_frame=True)
        logger.debug("successfully imported data as pandas df: \n {}".format(data_frame.describe()))
        return data_frame

    def tokenize_lemmatize(self, data, remove_stopwords=False, remove_special_characters=False, remove_urls=False,
                           skip_hashtags=False):
        logger.debug("tokenizing, lemmatizing and filtering words...")
        tknzr = TweetTokenizer()
        wnl = WordNetLemmatizer()
        language = config.get('TWITTER', 'language')
        language_map = {'de': 'german', 'en': 'english'}
        all_words = []
        filtered_list = []

        for index, row in data.iterrows():
            all_words.append([wnl.lemmatize(i, j[0].lower()) if j[0].lower() in ['a', 'n', 'v'] else wnl.lemmatize(i)
                              for i, j in pos_tag(tknzr.tokenize(row['text'].replace("\\n", " ").replace("'s", "")))])

        for sublist in all_words:
            for item in sublist:
                filtered_list.append(item)
        if remove_stopwords:
            filtered_list = [word for word in filtered_list if word.lower() not in
                             stopwords.words(language_map[language])]
        if remove_special_characters:
            filtered_list = [word for word in filtered_list if word.lower() not in
                             self.special_characters]
        if remove_urls:
            filtered_list = [word for word in filtered_list if not word.startswith('http')]
        if skip_hashtags:
            filtered_list = [word for word in filtered_list if word.lower() not in
                             [hashtag.lower() for hashtag in self.hashtags_list]]
        return filtered_list

    def count_words(self, list_of_words, top=40):
        counts = Counter(list_of_words).most_common(top)
        # convert list of tuples to dict for easier plotting
        dict_with_word_count = {}
        for v, k in counts:
            dict_with_word_count[v] = k
        # remove empty string -> ''
        dict_with_word_count.pop('', None)  # doesn't work!?
        logger.debug("word count ranking: {}".format(dict_with_word_count))
        return dict_with_word_count

    def plot_bar_diagram_from_dict(self, data, save_plot_file_name=False):
        names = list(data.keys())
        values = list(data.values())
        plt.bar(range(len(data)), values, tick_label=names, align='center')
        plt.xticks(rotation=85)
        if save_plot_file_name:
            plt.savefig(self.path_to_plots + str(get_time()) + str(self.file_name) + '.png')
        plt.show()


if __name__ == '__main__':
    file_to_analyze = "Trump.sqlite"
    analyze = Analyzer()
    df = analyze.get_sql_data(columns="text")
    tokenized_data = analyze.tokenize_lemmatize(df,
                                                remove_stopwords=True,
                                                remove_special_characters=True,
                                                remove_urls=True,
                                                skip_hashtags=True)
    word_counts = analyze.count_words(tokenized_data)
    analyze.plot_bar_diagram_from_dict(word_counts, save_plot_file_name=True)
