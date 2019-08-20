#coding=utf8

import re
import logging
import datetime
import dateutil.parser

import requests

import config


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
            minute=('minutes', d, config.hn_datetime_format),
            hour=('hours', d, config.hn_datetime_format),
            day=('days', d, config.hn_date_format),
            month=('days', d*30, config.hn_date_format),
    )

    for s, (k, v, f) in ms.items():
        if s in relative_time:
            return (now - datetime.timedelta(**{k:v})).strftime(f)
    return relative_time


def string_to_datetime(s):
    # return datetime.datetime.strptime(s, 
    #            config.hn_datetime_format if ':' in s else config.hn_date_format)
    return dateutil.parser.parse(s)


def get_post_identity(post):
    return post['url']


def format_url(url):
    return url if url[:4] == 'http' else '%s/%s' % (config.hn_domain, url)
