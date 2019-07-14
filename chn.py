#coding=utf8

import os
import time
import json
import math
import gzip
from urllib import request, parse
from bs4 import BeautifulSoup

import config


def crawle_reddit():
    items = {}
    if os.path.exists(config.reddit_data_file):
        print('Data file exists.')
        with open(config.reddit_data_file, 'r') as f:
            items = json.loads(f.read())

    for cat, urls in config.reddit_urls:
        if type(urls) == str:
            urls = (urls, )
        max_items_per_cat_url = math.ceil(config.max_items_per_cat / len(urls))

        cat_len = len(filter(lambda x: x[1]['cat'] == cat, items.items()))
        if cat_len >= config.skip_cat_when_large_then:
            print('Skip %s for count %s.' % (cat, cat_len))
            continue

        for url in urls:
            is_break = False
            next_url = url
            i = 0

            while not is_break:
                resp = open_url(cat, url)
                if resp is None:
                    print('Failed Crawle %s url: %s...' % (cat, url))
                    is_break = True
                    continue
                soup = parse_resp(resp)
                aas = soup.findAll(name='a', class_='title')

                for a in aas:
                    title = a.text
                    href = a.attrs['href']
                    if href in items:
                        continue
                    if 'alb.reddit.com' in href or 'on Slack!' in title:
                        continue

                    items[href] = dict(
                            title=title,
                            href=href,
                            cat=cat,
                        )
                    i += 1
                    if i == max_items_per_cat_url:
                        is_break = True

                next_btn = soup.select_one('span.next-button a')
                if next_btn:
                    next_url = next_btn.attrs['href']
                else:
                    print('%s reached end with %s items.' % (cat, len(items)))
                    is_break = True

                with open(config.reddit_data_file, 'w') as f:
                    f.write(json.dumps(items))


def open_url(cat, url)
    retry = 0

    while retry < config.max_retry:
        try:
            print('Crawle %s url: %s...' % (cat, url))
            req = request.Request(url, headers=config.reddit_headers)
            req.set_proxy(config.proxy_host, 'http')
            resp = request.urlopen(req)
            return resp
        except:
            retry += 1
            time.sleep(1.5)
            print('Retry %s time crawle %s url: %s...' % (retry, cat, url))

    return None


def parse_resp(resp):
    gf = gzip.GzipFile(fileobj=resp)
    html = gf.read()
    soup = BeautifulSoup(html.decode('utf8'))
    return soup
