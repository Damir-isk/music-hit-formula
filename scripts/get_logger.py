import inspect
import logging
import logging.config
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    directory = Path(__file__).parent.parent / 'logs'
    directory.mkdir(exist_ok=True)
    filename = Path(inspect.currentframe().f_back.f_code.co_filename).stem
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'main': {
                'format': '%(asctime)s [%(levelname)s]: %(message)s',
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
                'level': 'DEBUG',
                'formatter': 'main',
                'filename': str(directory / f'{filename}.log'),
                'encoding': 'utf8',
            },
        },
        'root': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
    logging.config.dictConfig(config)
    return logging.getLogger(name)
