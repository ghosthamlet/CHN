#coding=utf8

import os
import re
import time
import json
import csv
import math
import gzip
import zlib
import shutil
import datetime
import logging

from urllib.parse import urlparse
from urllib import request, parse
from bs4 import BeautifulSoup

import config
import extract_text as et
import requests
import pickle

import numpy as np
from train import *


logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger('crawler')

fileHandler = logging.FileHandler("{0}/{1}.log".format('data', 'ui'))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

# consoleHandler = logging.StreamHandler()
# consoleHandler.setFormatter(logFormatter)
# logger.addHandler(consoleHandler)
logger.setLevel(logging.INFO)


def crawle_reddit():
    items = {}
    if os.path.exists(config.reddit_json_file):
        print('Data file exists.')
        with open(config.reddit_json_file, 'r') as f:
            items = json.loads(f.read())

    for cat, urls in config.reddit_urls:
        if type(urls) == str:
            urls = (urls, )
        max_items_per_cat_url = math.ceil(config.max_items_per_cat / len(urls))

        cat_len = len(list(filter(lambda x: x[1]['cat'] == cat, items.items())))
        if cat_len >= config.skip_cat_when_large_then:
            print('Skip %s for count %s.' % (cat, cat_len))
            continue

        for url in urls:
            is_break = False
            next_url = url
            i = 0

            while not is_break:
                resp, err_msg = open_url(cat, next_url)
                if resp is None:
                    is_break = True
                    continue
                soup = parse_resp(resp)
                aas = soup.findAll(name='a', class_='title')

                for a in aas:
                    title = a.text
                    href = a.attrs['href']
                    if href in items:
                        if 'href' in items[href]:
                            del items[href]['href']
                        continue
                    if 'alb.reddit.com' in href or 'on Slack!' in title:
                        continue

                    items[href] = dict(
                            title=title,
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

                with open(config.reddit_json_file, 'w') as f:
                    f.write(json.dumps(items))

class HnData:
    def __init__(self):
        self.pages = dict(
                hot={
                    'url': '/',
                    'saved': 'data/hn_hot.json',
                    'max_page': 1,
                    'login': False,
                    }, 
                lastest={
                    'url': '/newest',
                    'saved': 'data/hn_lastest.json',
                    'max_page': 10,
                    'login': False,
                    }, 
                past={
                    'url': '/front',
                    'saved': 'data/hn_past.json',
                    'max_page': 20,
                    'login': False,
                    }, 
                ask={
                    'url': '/ask',
                    'saved': 'data/hn_ask.json',
                    'max_page': 20,
                    'login': False,
                    },
                show={
                    'url': '/show',
                    'saved': 'data/hn_show.json',
                    'max_page': 20,
                    'login': False,
                    },
                jobs={
                    'url': '/jobs',
                    'saved': 'data/hn_jobs.json',
                    'max_page': 20,
                    'login': False,
                    },
                submitted={
                    'url': '/submitted?id=%s',
                    'saved': 'data/hn_submitted.json',
                    'max_page': 0,
                    'login': True,
                    }, 
                upvoted={
                    'url': '/upvoted?id=%s',
                    'saved': 'data/hn_upvoted.json',
                    'max_page': 0,
                    'login': True,
                    }, 
                favorite={
                    'url': '/favorites?id=%s',
                    'saved': 'data/hn_favorite.json',
                    'max_page': 0,
                    'login': True,
                    },
                )

        self.all_posts = {k: {} for k in self.pages}

    def load_posts(self, page_type):
        with open(self.pages[page_type]['saved'], 'r') as f:
            self.all_posts[page_type] = json.loads(f.read())


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


# https://github.com/nicksergeant/hackernews/blob/master/hackernews.py
class HnCrawler:
    def __init__(self):
        self.cookies = None
        self.cookie_file = os.path.join('data', 'hn.cookie')
        self.hn_data = HnData()

        self.domain = 'https://news.ycombinator.com'
        self.proxy_dict = { 
              'http': config.proxy_host, 
              'https': config.proxy_host, 
            }

        if os.path.exists(self.cookie_file):
            with open(self.cookie_file, 'br') as f:
                self.cookies = pickle.load(f)

    def login(self, username, password):
        data = {
                'acct': username,
                'pw': password,
                }
        r = self.request('post', '/login', data=data)
        if b'type="password"' in r.content:
            return False

        self.cookies = r.cookies #.decode()

        with open(self.cookie_file, 'bw+') as f:
            pickle.dump(self.cookies, f)
        return True

    def get_username(self):
        if self.cookies:
            return self.cookies.get('user').split('&')[0]

        return ''

    def crawle(self, url):
        r = self.request('get', url)
        return r

    def save_all(self):
        for k, v in self.hn_data.pages.items():
            self.save(v['url'], k)

    def save(self, url, page_type, 
             page=0, incremental=False, refresh=False):
        page_meta = self.hn_data.pages[page_type]
        max_page = page_meta['max_page']
        if max_page > 0 and page == max_page:
            return

        r = self.crawle(url)
        if r is None:
            return
        
        soup = parse_resp(r)
        athing_els = soup.select('.athing')
        subtext_els = soup.select('.subtext')
        title_els = soup.select('.storylink')
        rank_els = soup.select('.rank')
        age_els = soup.select('.age')
        comment_els = soup.select('.subtext')
        more_el = soup.select('.morelink')
        end_request = False

        posts = []
        latest_post = None
        json_file = page_meta['saved']
        if not refresh and os.path.exists(json_file):
            with open(json_file, 'r') as f:
                posts = json.loads(f.read())
                latest_post = posts[0]
            if incremental:
                posts.reverse()

        logger.info('---')
        logger.info(page_type)
        logger.info(len(title_els))
         
        for i, t in enumerate(title_els):
           # if t.atts['href'] in posts:
           #    continue

            url = t.attrs['href']
            c_cnt = 0
            c_url = ''
            c_el = comment_els[i].select('a')[-1]
            if 'comment' in c_el.text:
                c_cnt = int(c_el.text.split('\xa0')[0])
                c_url = c_el.attrs['href']
            if 'discuss' in c_el.text:
                c_url = c_el.attrs['href']
            site_el = athing_els[i].select_one('.sitebit')
            score_el = subtext_els[i].select_one('.score')
            author_el = subtext_els[i].select_one('.hnuser')
            age = absolute_time(age_els[i].text)

            logger.info('---')
            logger.info(page_type)
            logger.info(url)

            if incremental and latest_post and url == latest_post['url']:
                end_request = True
                break

            posts.append(dict(
                    url=url,
                    title=t.text,
                    rank=int(rank_els[i].text[:-1]),
                    site=site_el.text if site_el else '',
                    score=int(score_el.text.split(' ')[0]) if score_el else 0,
                    auther=author_el.text if author_el else '',
                    age=age,
                    comment_cnt=c_cnt,
                    comment_url=c_url,
            ))

        with open(json_file, 'w') as f:
            if incremental:
                posts.reverse()
            f.write(json.dumps(posts))

        if more_el and not end_request:
            url = more_el[0].attrs['href']
            self.save('/%s' % url, page_type, 
                    page+1, incremental=incremental, refresh=False)

    def can_incremental(self, page_type):
        page_meta = self.hn_data.pages[page_type]
        json_file = page_meta['saved']
        return page_meta['login'] and os.path.exists(json_file)

    def request(self, method, url, data=None):
        kwargs = dict(
                # login post will response cookie, if follow redirect, can't get that cookie
                allow_redirects=False,
                proxies=self.proxy_dict
        )
        if data is not None:
            kwargs['data'] = data
        if self.cookies is not None:
            kwargs['cookies'] = self.cookies

        return getattr(requests, method)(self.full_url(url), **kwargs)

    def full_url(self, url):
        return '%s%s' % (self.domain, url)


class HnAnalyze:
    def __init__(self):
        # have to run this line in __main__ module??
        # from train import *
        with open('data/LinearSVC_model.pkl', 'rb') as f:
            self.model = pickle.load(f)

    def assoc_cat(self, posts):
        for v in posts:
            cat = self.classify([v['title']])[0]
            v['cat'] = cat

    def classify(self, titles):
        return self.model.predict(titles)
      # probs = self.model.decision_function(titles)
      # idxs = np.argsort(probs)[0][-3:][::-1]
      # return self.model.classes_[idxs]

    def maybe_upvote(self, post, upvoted_posts):
        """check if post cat is in upvoted_posts most common cats,
        TODO: get posts in hot/lastest created older then latest upvoted but not in upvoted, 
              tag as non_upvote, train with upvoted"""

    def maybe_favorite(self, post, favorite_posts):
        """check if post cat is in favorite_posts most common cats,
        TODO: get posts in hot/lastest created older then latest favorite but not in favorite, 
              tag as non_favorite, train with favorite"""

    def most_common_cats(self, posts):
        pass


class HnSearch:
    def __init__(self):
        pass
    

def open_url(cat, url):
    retry = 0
    headers = config.reddit_headers
    if 'reddit.com' not in url:
        headers = {}
        for k, v in config.reddit_headers.items():
            if k == 'Cookie':
                continue
            headers[k] = v
        headers['Host'] = urlparse(url).netloc

    while retry < config.max_retry:
        try:
            print('Crawle %s url: %s...' % (cat, url))
            req = request.Request(url, headers=headers)
            req.set_proxy(config.proxy_host, 'http')
            resp = request.urlopen(req, timeout=6)
            return resp, None
        except Exception as e:
            err_msg = getattr(e, 'code', getattr(e, 'reason', str(e)))
            # XXX: catch timeout/ctrl-c ...
            retry += 1
            time.sleep(1.5)
            print(e, headers)
            print('Retry %s time crawle %s url: %s...' % (retry, cat, url))

    print('Failed Crawle %s webpage: %s...' % (cat, url))
    return None, err_msg


def parse_resp(resp):
    if type(resp) == requests.models.Response:
        return BeautifulSoup(resp.content, features="lxml")

    zip_type = resp.headers.get('content-encoding', '')
    if zip_type  == 'deflate':
        try:
            html = zlib.decompress(resp.read())
        except:
            print('!!! Response encoding failed.')
            return  None
    elif zip_type  == 'gzip':
        try:
            gf = gzip.GzipFile(fileobj=resp)
            html = gf.read()
        except:
            print('!!! Response encoding failed.')
            return  None
    elif zip_type  == 'br':
        print('!!! Response encoding: br.')
        return None
    else:
        html = resp.read()

    try:
        soup = BeautifulSoup(html.decode('utf8'))
    except:
        print('!!! Response html parse failed.')
        return None
    return soup


# https://realpython.com/python-csv/
def reddit_json_to_csv():
    with open(config.reddit_json_file, 'r') as f:
        json_dict = json.loads(f.read())
    with open(config.reddit_csv_file, 'w') as f:
        fieldnames = ['title', 'url', 'cat', 'text']
        w = csv.DictWriter(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
        w.writeheader()
        for url, d in json_dict.items():
            if 'href' in d:
                del d['href']
            w.writerow({**d, 'url': url})


def save_webpage_text():
    with open(config.reddit_json_file, 'r') as f:
        json_dict = json.loads(f.read())

    try:
        for i, (url, d) in enumerate(json_dict.items()):
            is_reddit_page = False
            is_continue = False
            cat = d['cat']
            url = url.lower()
            d['webpage_status'] = '200'

            if 'text' in d:
                continue

            # for retry
            if d['webpage_status'] != '200':
                d['text'] = ''
                continue

            if d['cat'] in config.reddit_skip_text_cat:
                d['webpage_status'] = 'skip_cat'
                d['text'] = ''
                continue

            for domain in config.reddit_skip_text_domain:
                if domain in url:
                    is_continue = True
                    d['webpage_status'] = 'skip_domain'
                    d['text'] = ''
                    break

            for ext in ['.pdf', '.doc', '.docx', '.xls', '.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                if ext in url:
                    is_continue = True
                    d['webpage_status'] = 'skip_ext'
                    d['text'] = ''
                    break

            if is_continue:
                continue

            if url[0] == '/':
                is_reddit_page = True
                url = 'https://www.reddit.com' + url

            resp, err_msg = open_url(cat, url)
            if resp is None:
                d['webpage_status'] = str(err_msg)
                d['text'] = ''
                continue

            soup = parse_resp(resp)
            if soup is None:
                d['webpage_status'] = 'html_parse_error'
                d['text'] = ''
                continue

            if is_reddit_page:
                desc_el = soup.select_one('.expando .usertext-body')
                text = desc_el and desc_el.text.strip() or ''
                if not text:
                    first_cmt_el = soup.select_one('.nestedlisting .usertext-body')
                    text = first_cmt_el and first_cmt_el.text.strip() or ''
                print('==================reddit page======================')
            else:
                print('==================other page======================')
                text = et.extract(soup)[0].strip()
            print(text[:30], '...', text[-30:])
            d['text'] = text
            print('')

            if i > 0 and i % 10 == 0:
                shutil.copy(config.reddit_json_file, config.reddit_json_file + '.bak')
                with open(config.reddit_json_file, 'w') as f:
                    f.write(json.dumps(json_dict))
    finally:
        shutil.copy(config.reddit_json_file, config.reddit_json_file + '.bak')
        with open(config.reddit_json_file, 'w') as f:
            f.write(json.dumps(json_dict))

