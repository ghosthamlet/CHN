#coding=utf8

import os
import time
import json
import csv
import math
import gzip
import zlib
import shutil

from urllib.parse import urlparse
from urllib import request, parse
from bs4 import BeautifulSoup

import config
import extract_text as et
import requests
import pickle


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
                    'url': '',
                    'saved': 'data/hn_hot.json',
                    }, 
                lastest={
                    'url': '',
                    'saved': 'data/hn_lastest.json',
                    }, 
                submitted={
                    'url': '',
                    'saved': 'data/hn_submitted.json',
                    }, 
                upvoted={
                    'url': '',
                    'saved': 'data/hn_upvoted.json',
                    }, 
                favorite={
                    'url': '',
                    'saved': 'data/hn_favorite.json',
                    },
                )

        self.all_posts = {k: {} for k in self.pages}

    def load_posts(self, page_type):
        with open('data/hn_%.json' % page_type, 'r') as f:
            self.all_posts[page_type] = json.loads(f.read())


# https://github.com/nicksergeant/hackernews/blob/master/hackernews.py
class HnCrawler:
    def __init__(self):
        self.max_page = 1

        self.cookies = None
        self.cookie_file = os.path.join('data', 'hn.cookie')
        self.hn_data = HnData()

        self.domain = 'https://news.ycombinator.com'
        self.proxy_dict = { 
              'http': config.proxy_host, 
              'https': config.proxy_host, 
            }

    def login(self, acct, pw):
        data = {
                'acct': acct,
                'pw': pw,
                }
        r = self.request('post', '/login', data=data)
        self.cookies = r.cookies #.decode()

        with open(self.cookie_file, 'bw+') as f:
            pickle.dump(self.cookies, f)

    def crawle(self, url):
        r = self.request('get', url)
        return r

    def save_all(self):
        for k, v in self.hn_data.pages.items():
            self.save(v['url'], k)

    def save(self, url, page_type, page=0):
        if page == self.max_page:
            return

        r = self.crawle(url)
        if r is None:
            return
        
        soup = parse_resp(r)
        title_els = soup.select('.storylink')
        site_els = soup.select('.sitebit')
        rank_els = soup.select('.rank')
        score_els = soup.select('.score')
        author_els = soup.select('.hnuser')
        age_els = soup.select('.age')
        comment_els = soup.select('.subtext')
        more_el = soup.select('.morelink')

        posts = {}
        json_file = self.hn_data.pages[page_type]['saved']
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                posts = json.loads(f.read())
         
        for i, t in enumerate(title_els):
           # if t.atts['href'] in posts:
           #    continue

            c_cnt = 0
            c_url = ''
            c_el = comment_els[i].select('a')[-1]
            if 'comment' in c_el.text:
                c_cnt = int(c_el.text.split(' ')[0])
                c_url = c_el.attrs['href']
            if 'discuss' in c_el.text:
                c_url = c_el.attrs['href']

            posts[t.atts['href']] = dict(
                    title=t.text,
                    rank=rank_els[i].text[:-1],
                    site=site_els[i].text,
                    score=int(score_els[i].text.split(' ')[0]),
                    auther=author_els[i].text,
                    age=age[i].text,
                    comment_cnt=c_cnt,
                    comment_url=c_url,
            )

        with open(json_file, 'w') as f:
            f.write(json.dumps(posts))

        if more_el:
            url = more_el[0].attrs['href']
            self.save('/%s' % url, page_type, page+1)

    def request(self, method, url, data=None):
        kwargs = dict(
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
        with open('data/LinearSVC_model.pkl', 'rb') as f:
            self.model = pickle.load(f)

    def assoc_cat(self, posts):
        for k, v in posts.items():
            cat = self.classify(v['title'])
            v['cat'] = cat

    def classify(self, titles):
        return self.model.predict(titles)
        # return self.model.predict_proba(titles)

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
    

class HnConsole:
    def __init__(self, page_type):
        self.hn_data = HnData()
        self.hn_data.load_posts(page_type)


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
        return BeautifulSoup(resp.content)

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

