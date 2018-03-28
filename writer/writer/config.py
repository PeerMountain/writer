from os import getenv


BROKER_URL = getenv('BROKER_URL')
if not BROKER_URL:
    raise NotImplementedError('BROKER_URL must be configured.')

LOG_LEVEL = getenv('LOG_LEVEL', 'INFO')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s [%(name)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S:',
        }
    },
    'loggers': {
        'writer': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
        },
    },
}
