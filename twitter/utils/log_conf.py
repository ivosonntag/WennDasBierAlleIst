
def logging_dict(logging_level):
    # decide whether logging parameters are default or not
    format_console = "%(asctime)s - %(name)s - %(levelname)s - [thread:%(threadName)s] - %(message)s"
    log_dict = {
        'version': 1,
        'disable_existing_loggers': False,   # set True to suppress existing loggers from other modules
        'loggers': {
            'streamer': {
               'level': logging_level,
               'handlers': ['console'],
            },
            'helper': {
               'level': logging_level,
               'handlers': ['console'],
            },
            'data-sql': {
               'level': logging_level,
               'handlers': ['console'],
            },
            'data-file': {
               'level': logging_level,
               'handlers': ['console'],
            },
            'data-frame': {
               'level': logging_level,
               'handlers': ['console'],
            },
            'deletion-checker': {
               'level': logging_level,
               'handlers': ['console'],
            },
            'vizualize': {
               'level': logging_level,
               'handlers': ['console'],
            },
            'analyzer': {
               'level': logging_level,
               'handlers': ['console'],
            },
        },
        'formatters': {
            # install colored logs with 'pip install coloredlogs'
            'colored': {'()': 'coloredlogs.ColoredFormatter', 'format': format_console, 'datefmt': '%H:%M:%S'},
            'format_for_console': {'format': format_console, 'datefmt': '%m-%d %H:%M:%S'}
        },
        'handlers': {
            'console': {
                'level': logging_level,
                'class': 'logging.StreamHandler',
                'formatter': 'colored',
                'stream': 'ext://sys.stdout'
            },

        },
    }
    return log_dict
