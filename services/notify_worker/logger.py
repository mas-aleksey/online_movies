LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DEFAULT_HANDLERS = ('console',)


def get_logger_config(log_level):
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': LOG_FORMAT,
            },
        },
        'handlers': {
            'console': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            '': {
                'handlers': LOG_DEFAULT_HANDLERS,
                'level': log_level,
            }
        },
        'root': {
            'level': log_level,
            'formatter': 'verbose',
            'handlers': LOG_DEFAULT_HANDLERS,
        },
    }


def get_logger(name):
    import logging
    from logging import config as logging_config
    import settings

    log_level = 'DEBUG' if settings.DEBUG else 'INFO'
    LOGGING = get_logger_config(log_level)
    logging_config.dictConfig(LOGGING)

    return logging.getLogger(name)
