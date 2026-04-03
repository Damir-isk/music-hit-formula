import os
import logging.config

def setup_logging():
    log_dir = '../logs/'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'main': {
                'format': '%(asctime)s [%(levelname)s] %(filename)s: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'main',
            },
            'file': {
                'class': 'logging.FileHandler',
                'level': 'INFO',
                'formatter': 'main',
                'filename': os.path.join(log_dir, 'main.log'),
                'encoding': 'utf8',
            },
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': True
            },
        }
    }

    logging.config.dictConfig(logging_config)
