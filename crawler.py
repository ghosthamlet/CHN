#coding=utf8

import os
import csv
import gzip
import zlib
import math
import shutil
import time

from urllib.parse import urlparse
from urllib import request, parse

from bs4 import BeautifulSoup

import config

import extract_text as et


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

            if d['cat'] in config.reddit_skip_cat:
                d['webpage_status'] = 'skip_cat'
                d['text'] = ''
                continue

            for domain in config.reddit_skip_domain:
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


def parse_resp(resp):
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

