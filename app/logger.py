"""
logger.py
---------

This module configures the application logger using the colorlog package.
It sets up a colored log formatter for improved readability in the console
and provides a logger instance for use throughout the application.
"""

import logging
import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s[%(asctime)s] %(levelname)s %(filename)s:%(lineno)d '
    '%(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
))

logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)
