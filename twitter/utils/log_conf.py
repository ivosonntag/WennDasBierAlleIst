# logging configuration
def logging_dict(logger_name, logging_level):
    # decide whether logging parameters are default or not
    format_console = "%(asctime)s - %(name)s - %(levelname)s - [thread:%(threadName)s] - %(message)s"
    log_dict = {
        'version': 1,
        'disable_existing_loggers': False,   # set True to suppress existing loggers from other modules
        'loggers': {
            'tvizzer': {
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
