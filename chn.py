#coding=utf8

import os
import json
import logging

from bs4 import BeautifulSoup

import config
import requests
import pickle

import numpy as np
from train import *
import utils


logger = utils.get_logger()


class HnData:
    def __init__(self):
        self.pages = config.hn_pages
        self.all_posts = {k: [] for k in self.pages}

    def load_posts(self, page_type):
        fp = self.pages[page_type]['saved']
        if os.path.exists(fp):
            with open(fp, 'r') as f:
                self.all_posts[page_type] = json.loads(f.read())

    def remove_post(self, page_type, post):
        posts = self.all_posts[page_type]
        posts = [v for v in posts 
                 if utils.get_post_identity(v) != utils.get_post_identity(post)]
        self.all_posts[page_type] = posts

        fp = self.pages[page_type]['saved']
        with open(fp, 'w') as f:
            f.write(json.dumps(posts))


# https://github.com/nicksergeant/hackernews/blob/master/hackernews.py
class HnClient:
    def __init__(self):
        self.cookies = None
        self.cookie_file = os.path.join('data', 'hn.cookie')
        self.hn_data = HnData()

        self.domain = config.hn_domain
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

    def get_all_posts(self):
        for k, v in self.hn_data.pages.items():
            self.download_posts(v['url'], k)

    def download_posts(self, url, page_type, 
            page=0, incremental=False, refresh=False):
        page_meta = self.hn_data.pages[page_type]
        max_page = page_meta['max_page']
        if max_page > 0 and page == max_page:
            return

        r = self.crawle(url)
        if r is None:
            return
        
        soup = BeautifulSoup(r.content, features="lxml")
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
            if len(comment_els) > i:
                c_el = comment_els[i].select('a')[-1]
                if 'comment' in c_el.text:
                    c_cnt = int(c_el.text.split('\xa0')[0])
                    c_url = c_el.attrs['href']
                if 'discuss' in c_el.text:
                    c_url = c_el.attrs['href']
            vote_el = athing_els[i].select_one('.votelinks')
            site_el = athing_els[i].select_one('.sitebit')
            score_el = None
            author_el = None
            if len(subtext_els) > i:
                score_el = subtext_els[i].select_one('.score')
                author_el = subtext_els[i].select_one('.hnuser')
            age = ''
            if len(age_els) > i:
                age = utils.absolute_time(age_els[i].text)
            vote_a_el = vote_el.select_one('a') if vote_el else None
            vote_url = vote_a_el.attrs['href'] if vote_a_el else ''

            logger.info('---')
            logger.info(page_type)
            logger.info(url)

            if incremental and latest_post and url == latest_post['url']:
                end_request = True
                break

            posts.append(dict(
                    url=url,
                    title=t.text,
                    # rank=int(rank_els[i].text[:-1]),
                    rank=0,
                    site=site_el.text if site_el else '',
                    score=int(score_el.text.split(' ')[0]) if score_el else 0,
                    auther=author_el.text if author_el else '',
                    age=age,
                    comment_cnt=c_cnt,
                    comment_url=c_url,
                    vote_url='/%s' % vote_url,
                    # &un=t for unfavorite
                    favorite_url='/fave?%s' % vote_url.split('?')[1] if vote_url else ''
            ))

        with open(json_file, 'w') as f:
            if incremental:
                posts.reverse()
            f.write(json.dumps(posts))

        if more_el and not end_request:
            url = more_el[0].attrs['href']
            self.download_posts('/%s' % url, page_type, 
                    page+1, incremental=incremental, refresh=False)

    def can_incremental(self, page_type):
        page_meta = self.hn_data.pages[page_type]
        json_file = page_meta['saved']
        return page_meta['login'] and os.path.exists(json_file)

    def upvote(self, post, upvoted=False):
        url = post['vote_url']
        if upvoted:
            url = url.replace('how=up', 'how=un')
        return self.request('get', url)

    def favorite(self, post, favorited=False):
        url = post['favorite_url']
        if favorited:
            url += '&un=t'
        return self.request('get', url)

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
        cats = self.classify([v['title'] for v in posts])
        for i, v in enumerate(posts):
            # cat = self.classify([v['title']])[0]
            v['cat'] = cats[i]

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

