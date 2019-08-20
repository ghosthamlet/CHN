#coding=utf8

import re
import logging
import datetime

import requests


def get_logger(name=''):
    logger = logging.getLogger(name)
    file_handler = logging.FileHandler("{0}/{1}.log".format('data', 'ui'))
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"))
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger

    # logging.basicConfig(
    #     level=logging.INFO,
    #     format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    #     handlers=[
    #         logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
    #         logging.StreamHandler()
    #     ])


def absolute_time(relative_time):
    if not relative_time:
        return ''

    m = re.match('\d+', relative_time)
    if not m:
        return relative_time

    d = int(m[0])
    now = datetime.datetime.now()
    ms = dict(
            minute=('minutes', d, '%H:%M %b %d, %Y'),
            hour=('hours', d, '%H:%M %b %d, %Y'),
            day=('days', d, '%b %d, %Y'),
            month=('days', d*30, '%b %d, %Y'),
    )

    for s, (k, v, f) in ms.items():
        if s in relative_time:
            return (now - datetime.timedelta(**{k:v})).strftime(f)
    return relative_time


def get_post_identity(post):
    return post['url']
