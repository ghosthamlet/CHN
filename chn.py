#coding=utf8

import os
import time
import json
import math
import gzip
from urllib import request, parse
from bs4 import BeautifulSoup

proxy_host = '127.0.0.1:19180'
max_items_per_cat = 3000
max_retry = 6
reddit_urls = [
      #('life', 
      #    ('https://www.reddit.com/r/Life/', 
      #        'https://www.reddit.com/r/Life/top/')),
      #('literature', 
      #    ('https://www.reddit.com/r/literature/', 
      #            'https://www.reddit.com/r/literature/top/')),
      #('painting', 
      #    ('https://www.reddit.com/r/painting/', 
      #            'https://www.reddit.com/r/painting/top/')),
      ## failed
      ##('music', 
      ##    ('https://www.reddit.com/r/music/', 
      ##            'https://www.reddit.com/r/music/top/')),
      #('movie', 
      #        ('https://www.reddit.com/r/movies/', 
      #            'https://www.reddit.com/r/movies/top/')),
      #('scifi', 
      #    ('https://www.reddit.com/r/scifi/', 
      #        'https://www.reddit.com/r/scifi/top/')),
       ('dream', 
           ('https://www.reddit.com/r/Dream/', 
               'https://www.reddit.com/r/Dream/top/')),
       ('worldnews', 
           ('https://www.reddit.com/r/worldnews/', 
               'https://www.reddit.com/r/worldnews/top/')),
       ('environment', 
           ('https://www.reddit.com/r/environment/', 
               'https://www.reddit.com/r/environment/top/')),
       ('science', 
           ('https://www.reddit.com/r/science/', 
               'https://www.reddit.com/r/science/top/')),
       ('scientific_research', 
           ('https://www.reddit.com/r/scientificresearch/', 
               'https://www.reddit.com/r/scientificresearch/top/')),
       ('politics', 
           ('https://www.reddit.com/r/politics/', 
               'https://www.reddit.com/r/politics/top/')),

       ('programming', 
           ('https://www.reddit.com/r/programming/', 
               'https://www.reddit.com/r/programming/top/')),
       ('coding', 
           ('https://www.reddit.com/r/coding/', 
               'https://www.reddit.com/r/coding/top/')),
       ('computer_science', 
           ('https://www.reddit.com/r/compsci/', 
               'https://www.reddit.com/r/compsci/top/')),
       ('computing', 
           ('https://www.reddit.com/r/computing/', 
               'https://www.reddit.com/r/computing/top/')),
       ('csbook', 
           ('https://www.reddit.com/r/csbooks/', 
               'https://www.reddit.com/r/csbooks/top/')),
       ('software_architecture', 
           ('https://www.reddit.com/r/softwarearchitecture/', 
               'https://www.reddit.com/r/softwarearchitecture/top/')),
       ('hardware', 
           ('https://www.reddit.com/r/hardware/', 
               'https://www.reddit.com/r/hardware/top/')),
       # failed
       #('compiler', 
       #    ('https://www.reddit.com/r/compilers/', 
       #        'https://www.reddit.com/r/compilers/top/')),
        ('gamedev', 
            ('https://www.reddit.com/r/gamedev/', 
                'https://www.reddit.com/r/gamedev/top/')),
        ('devops', 
            ('https://www.reddit.com/r/devops/', 
                'https://www.reddit.com/r/devops/top/')),
        ('cloud_computing', 
            ('https://www.reddit.com/r/cloudcomputing/', 
                'https://www.reddit.com/r/cloudcomputing/top/')),
        ('hacker_news', 
            ('https://www.reddit.com/r/hackernews/', 
                'https://www.reddit.com/r/hackernews/top/')),
        ('visualization', 
            ('https://www.reddit.com/r/visualization/', 
                'https://www.reddit.com/r/visualization/top/')),

        ('math', 
            ('https://www.reddit.com/r/math/', 
                'https://www.reddit.com/r/math/top/')),
        ('crypto', 
            ('https://www.reddit.com/r/crypto/', 
                'https://www.reddit.com/r/crypto/top/')),
        ('algorithm', 
            ('https://www.reddit.com/r/algorithms/', 
                'https://www.reddit.com/r/algorithms/top/')),
        ('tiny_code', 
            ('https://www.reddit.com/r/tinycode/', 
                'https://www.reddit.com/r/tinycode/top/')),
        ('logic', 
            ('https://www.reddit.com/r/logic/', 
                'https://www.reddit.com/r/logic/top/')),

        ('linux', 
            ('https://www.reddit.com/r/linux/', 
                'https://www.reddit.com/r/linux/top/')),
        ('unix', 
            ('https://www.reddit.com/r/unix/', 
                'https://www.reddit.com/r/unix/top/')),
        ('macos', 
            ('https://www.reddit.com/r/MacOS/', 
                'https://www.reddit.com/r/MacOS/top/')),
        ('windows', 
            ('https://www.reddit.com/r/windows/', 
                'https://www.reddit.com/r/windows/top/')),
        ('android', 
            ('https://www.reddit.com/r/androiddev/', 
                'https://www.reddit.com/r/androiddev/top/')),
        ('ios', 
            ('https://www.reddit.com/r/ios/', 
                'https://www.reddit.com/r/ios/top/')),
        ('osdev', 
            ('https://www.reddit.com/r/osdev/', 
                'https://www.reddit.com/r/osdev/top/')),
        ('docker', 
            ('https://www.reddit.com/r/docker/', 
                'https://www.reddit.com/r/docker/top/')),
        ('unikernel', 
            ('https://www.reddit.com/r/UniKernel/', 
                'https://www.reddit.com/r/UniKernel/top/')),
        ('sysadmin', 
            ('https://www.reddit.com/r/sysadmin/', 
                'https://www.reddit.com/r/sysadmin/top/')),
        ('raspberry_pi', 
            ('https://www.reddit.com/r/raspberry_pi/',
                'https://www.reddit.com/r/raspberry_pi/top/', 
                'https://www.reddit.com/r/raspberrypi/top/', 
                'https://www.reddit.com/r/RASPBERRY_PI_PROJECTS/top/')),
        ('arduino', 
            ('https://www.reddit.com/r/arduino/', 
                'https://www.reddit.com/r/arduino/top/')),

        ('ai', 
            ('https://www.reddit.com/r/artificial/', 
                'https://www.reddit.com/r/artificial/top/')),
        ('agi', 
            ('https://www.reddit.com/r/agi/', 
                'https://www.reddit.com/r/agi/top/', 
                'https://www.reddit.com/r/GeneralAIChallenge/top/')),
        ('big_data', 
            ('https://www.reddit.com/r/bigdata/', 
                'https://www.reddit.com/r/bigdata/top/')),
        ('machine_learning', 
            ('https://www.reddit.com/r/MachineLearning/', 
                'https://www.reddit.com/r/MachineLearning/top/')),
        ('deep_learning', 
            ('https://www.reddit.com/r/deeplearning/', 
                'https://www.reddit.com/r/deeplearning/top/')),
        ('statistics', 
            ('https://www.reddit.com/r/statistics/', 
                'https://www.reddit.com/r/statistics/top/')),
        ('data_science', 
            ('https://www.reddit.com/r/datascience/', 
                'https://www.reddit.com/r/datascience/top/')),
        ('nlp', 
            ('https://www.reddit.com/r/LanguageTechnology/', 
                'https://www.reddit.com/r/LanguageTechnology/top/')),
        ('computer_vision', 
            ('https://www.reddit.com/r/computervision/', 
                'https://www.reddit.com/r/computervision/top/')),
        ('computer_sound', 
                ('https://www.reddit.com/r/audioengineering/',
                    'https://www.reddit.com/r/audioengineering/top/', 
                    'https://www.reddit.com/r/DSP/top/')),
        ('robotics', 
            ('https://www.reddit.com/r/robotics/', 
                'https://www.reddit.com/r/robotics/top/')),
        ('futurology', 
            ('https://www.reddit.com/r/Futurology/', 
                'https://www.reddit.com/r/Futurology/top/')),
        ('causality', 
            ('https://www.reddit.com/r/causality/', 
                'https://www.reddit.com/r/causality/top/')),

        ('i2p', 
            ('https://www.reddit.com/r/i2p/', 
                'https://www.reddit.com/r/i2p/top/')),
        ('tor', 
            ('https://www.reddit.com/r/TOR/', 
                'https://www.reddit.com/r/TOR/top/')),
        ('p2p', 
            ('https://www.reddit.com/r/P2P/', 
                'https://www.reddit.com/r/P2P/top/')),
        ('decentralization', 
                ('https://www.reddit.com/r/decentralization/',
                    'https://www.reddit.com/r/decentralization/top/', 
                    'https://www.reddit.com/r/Rad_Decentralization/top/',
                    'https://www.reddit.com/r/DistributedComputing/top/')),
        ('privacy', 
            ('https://www.reddit.com/r/Privacy/', 
                'https://www.reddit.com/r/Privacy/top/')),
        ('bitcoin', 
            ('https://www.reddit.com/r/Bitcoin/', 
                'https://www.reddit.com/r/Bitcoin/top/')),
        ('ethereum', 
            ('https://www.reddit.com/r/ethereum/', 
                'https://www.reddit.com/r/ethereum/top/')),
        ('eos', 
            ('https://www.reddit.com/r/eos/', 
                'https://www.reddit.com/r/eos/top/')),
        ('crypto_currency', 
            ('https://www.reddit.com/r/CryptoCurrency/', 
                'https://www.reddit.com/r/CryptoCurrency/top/')),

        ('datasets', 
            ('https://www.reddit.com/r/datasets/', 
                'https://www.reddit.com/r/datasets/top/')),
        ('nosql', 
            ('https://www.reddit.com/r/nosql/', 
                'https://www.reddit.com/r/nosql/top/')),
        ('database', 
            ('https://www.reddit.com/r/Database/', 
                'https://www.reddit.com/r/Database/top/')),

        ('asm', 
            ('https://www.reddit.com/r/asm/', 
                'https://www.reddit.com/r/asm/top/')),
        ('c', 
            ('https://www.reddit.com/r/C_Programming/', 
                'https://www.reddit.com/r/C_Programming/top/')),
        ('cpp', 
            ('https://www.reddit.com/r/cpp/', 
                'https://www.reddit.com/r/cpp/top/')),
        ('go', 
            ('https://www.reddit.com/r/golang/', 
                'https://www.reddit.com/r/golang/top/')),
        ('rust', 
            ('https://www.reddit.com/r/rust/', 
                'https://www.reddit.com/r/rust/top/')),
        ('java', 
            ('https://www.reddit.com/r/java/', 
                'https://www.reddit.com/r/java/top/')),
        ('scala', 
            ('https://www.reddit.com/r/scala/', 
                'https://www.reddit.com/r/scala/top/')),
        ('ocaml', 
            ('https://www.reddit.com/r/ocaml/', 
                'https://www.reddit.com/r/ocaml/top/')),
        ('sml', 
            ('https://www.reddit.com/r/sml/', 
                'https://www.reddit.com/r/sml/top/')),
        ('haskell', 
            ('https://www.reddit.com/r/haskell/', 
                'https://www.reddit.com/r/haskell/top/')),
        ('kotlin', 
            ('https://www.reddit.com/r/Kotlin/', 
                'https://www.reddit.com/r/Kotlin/top/')),
        ('swift', 
            ('https://www.reddit.com/r/swift/', 
                'https://www.reddit.com/r/swift/top/')),
        ('objective_c', 
            ('https://www.reddit.com/r/ObjectiveC/', 
                'https://www.reddit.com/r/ObjectiveC/top/')),

        ('apl', 
            ('https://www.reddit.com/r/apljk/', 
                'https://www.reddit.com/r/apljk/top/')),
        ('lisp', 
            ('https://www.reddit.com/r/lisp/', 
                'https://www.reddit.com/r/lisp/top/')),
        ('common_lisp', 
            ('https://www.reddit.com/r/Common_Lisp/', 
                'https://www.reddit.com/r/Common_Lisp/top/')),
        ('clojure', 
            ('https://www.reddit.com/r/Clojure/', 
                'https://www.reddit.com/r/Clojure/top/')),
        ('scheme', 
            ('https://www.reddit.com/r/scheme/', 
                'https://www.reddit.com/r/scheme/top/')),
        ('prolog', 
            ('https://www.reddit.com/r/prolog/', 
                'https://www.reddit.com/r/prolog/top/')),
        ('forth', 
            ('https://www.reddit.com/r/Forth/', 
                'https://www.reddit.com/r/Forth/top/')),
        ('smalltalk', 
            ('https://www.reddit.com/r/smalltalk/', 
                'https://www.reddit.com/r/smalltalk/top/')),
        ('erlang', 
            ('https://www.reddit.com/r/erlang/', 
                'https://www.reddit.com/r/erlang/top/')),
        ('r', 
            ('https://www.reddit.com/r/Rlanguage/', 
                'https://www.reddit.com/r/Rlanguage/top/')),
        ('julia', 
            ('https://www.reddit.com/r/Julia/', 
                'https://www.reddit.com/r/Julia/top/')),
        ('python', 
            ('https://www.reddit.com/r/Python/', 
                'https://www.reddit.com/r/Python/top/')),
        ('php', 
            ('https://www.reddit.com/r/PHP/', 
                'https://www.reddit.com/r/PHP/top/')),
        ('perl', 
            ('https://www.reddit.com/r/perl/', 
                'https://www.reddit.com/r/perl/top/')),
        ('ruby', 
            ('https://www.reddit.com/r/ruby/', 
                'https://www.reddit.com/r/ruby/top/')),
        ('lua', 
            ('https://www.reddit.com/r/lua/', 
                'https://www.reddit.com/r/lua/top/')),
        ('javascript', 
            ('https://www.reddit.com/r/javascript/', 
                'https://www.reddit.com/r/javascript/top/')),
        ('bash', 
            ('https://www.reddit.com/r/bash/', 
                'https://www.reddit.com/r/bash/top/')),
        ('tcl', 
            ('https://www.reddit.com/r/Tcl/', 
                'https://www.reddit.com/r/Tcl/top/')),
        ('css', 
            ('https://www.reddit.com/r/css/', 
                'https://www.reddit.com/r/css/top/')),
        ('html', 
            ('https://www.reddit.com/r/HTML/', 
                'https://www.reddit.com/r/HTML/top/')),

        ('vim', 
            ('https://www.reddit.com/r/vim/', 
                'https://www.reddit.com/r/vim/top/')),
        ('emacs', 
            ('https://www.reddit.com/r/emacs/', 
                'https://www.reddit.com/r/emacs/top/')),
        ('vscode', 
            ('https://www.reddit.com/r/vscode/', 
                'https://www.reddit.com/r/vscode/top/')),
        ('intellij_idea', 
            ('https://www.reddit.com/r/IntelliJIDEA/', 
                'https://www.reddit.com/r/IntelliJIDEA/top/')),
        ('git', 
            ('https://www.reddit.com/r/git/', 
                'https://www.reddit.com/r/git/top/')),
        ('programming_tools', 
            ('https://www.reddit.com/r/programmingtools/', 
                'https://www.reddit.com/r/programmingtools/top/')),
        ]


def crawle_reddit():
    items = {}
    data_file_path = 'data/reddit.json'

    if os.path.exists(data_file_path):
        print('Data file exists.')
        with open(data_file_path, 'r') as f:
            items = json.loads(f.read())

    for cat, urls in reddit_urls:
        if type(urls) == str:
            urls = (urls, )
        max_items_per_cat_url = math.ceil(max_items_per_cat / len(urls))

        for url in urls:
            is_break = False
            next_url = url
            i = 0

            while not is_break:
                resp = open_url(cat, url)
                gzipFile = gzip.GzipFile(fileobj=resp)
                html = gzipFile.read()
                soup = BeautifulSoup(html.decode('utf8'))
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

                with open(data_file_path, 'w') as f:
                    f.write(json.dumps(items))


def open_url(cat, url)
    retry = 0
    headers = {
            'Host': 'www.reddit.com',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
             # this have to ungzip
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cookie': 'loid=0000000000000401xj.2.1271292571569.Z0FBQUFBQmExR2o0c0J1WGtnQmUtd1otV19iNWphYUs0RTRHVzRTdDVaaVV1LThSaFRWeU5jLW15aFFhalFzYmpsY25FNF9oc21DOXFNTG5LSlZKU2tFZGdXbGxDZ29ObXV3RGpsUkx4d0lpOW9xZ2xWcWxHOFhoaHY4ZGNOekhybHNhTlA4X1F1T2M; edgebucket=sNsloB62V2ExNKdjXf; _ga=GA1.2.10112006.1523868326; __utma=55650728.10112006.1523868326.1539333330.1544603202.156; __gads=ID=88bf70d20a8b3dba:T=1523868331:S=ALNI_MZJ_D2twhkmVjOJNu8odDkfGHORBw; reddaid=3CDP5KVPWTONLTIB; reddit_session=6720967%2C2018-04-23T12%3A03%3A43%2C179943dd5efe602d9b871210c5ac62c4cba2a36d; uapp_cookie=3%3A1527210000; recent_srs=t5_2r3gv%2Ct5_2qkgk%2Ct5_2slz7%2Ct5_2z2bg%2Ct5_2sf8v%2Ct5_2vssy%2Ct5_2qhn4%2Ct5_2qhij%2Ct5_2qkfg%2Ct5_2t5eh; rseor3=; rabt=; token=eyJhY2Nlc3NUb2tlbiI6IjY3MjA5NjctcXNfbHBkVmNyMFVERFBqZHVQTDVjU1dmTkU0IiwidG9rZW5UeXBlIjoiYmVhcmVyIiwiZXhwaXJlcyI6MTU2MzEwNjAyMzQxOSwicmVmcmVzaFRva2VuIjoiNjcyMDk2Ny1mS19HUGRXejYtM01ZbXQwOVRYS1B5ejNkclEiLCJzY29wZSI6IiogZW1haWwiLCJ1bnNhZmVMb2dnZWRPdXQiOmZhbHNlfQ==.2; pc=uw; session_tracker=Z9w5GWUgWvR8hhTTwa.0.1563102662772.Z0FBQUFBQmRLdzNHaUF5YkpYMWt1M20yYWJOb3J6NXlvb1ltVFlBWnlKRE9KdGNWdTFnLVJuMHpzdUQxWnZjVnUxMlY4Uy12dVZJUjRfQ0ZwWGhVY3Q5QV9jQkU5RDBLandDVElRVkd3VjB3RTJjSTVyc21oYnlrZ2V6T0Z0al83R25RNUNkaEZkSzg; aasd=1%7C1563102521145; __aaxsc=0; ghosthamlet_recentclicks2=t3_cbfk2o%2Ct3_cd0osl%2Ct3_4huuud%2C; theme=daymode; compact=true; over18=true',
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'Trailers',
            }

    while retry < max_retry:
        try:
            print('Crawle %s url: %s...' % (cat, url))
            req = request.Request(url, headers=headers)
            req.set_proxy(proxy_host, 'http')
            resp = request.urlopen(req)
            return resp
        except:
            retry += 1
            time.sleep(1.5)
            print('Retry %s time crawle %s url: %s...' % (retry, cat, url))


