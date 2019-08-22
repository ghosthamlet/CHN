#coding=utf8

app_name = 'CHN'
proxy_host = '127.0.0.1:19180'
hn_domain = 'https://news.ycombinator.com'
hn_datetime_format = '%H:%M %b %d, %Y'
hn_date_format = '%b %d, %Y'
hn_recommend_compare = 100
hn_classifer_model = 'data/LinearSVC_model.pkl'

hn_pages = dict(
        recommend={
            'url': '/newest',
            'saved': 'data/hn_recommend.json',
            #'max_page': 10,
            'max_page': 3,
            'login': True,
            },
        hot={
            'url': '/',
            'saved': 'data/hn_hot.json',
            'max_page': 1,
            'login': False,
            }, 
        latest={
            'url': '/newest',
            'saved': 'data/hn_latest.json',
            #'max_page': 10,
            'max_page': 3,
            'login': False,
            }, 
        past={
            'url': '/front',
            'saved': 'data/hn_past.json',
            #'max_page': 10,
            'max_page': 3,
            'login': False,
            }, 
        ask={
            'url': '/ask',
            'saved': 'data/hn_ask.json',
            #'max_page': 10,
            'max_page': 3,
            'login': False,
            },
        show={
            'url': '/show',
            'saved': 'data/hn_show.json',
            #'max_page': 10,
            'max_page': 3,
            'login': False,
            },
        jobs={
            'url': '/jobs',
            'saved': 'data/hn_jobs.json',
            #'max_page': 10,
            'max_page': 3,
            'login': False,
            },
        submitted={
            'url': '/submitted?id=%s',
            'saved': 'data/hn_submitted.json',
            # 0 to get all this type pages
            # 'max_page': 0,
            'max_page': 10,
            'login': True,
            }, 
        upvoted={
            'url': '/upvoted?id=%s',
            'saved': 'data/hn_upvoted.json',
            # 0 to get all this type pages
            # 'max_page': 0,
            'max_page': 10,
            'login': True,
            }, 
        favorite={
            'url': '/favorites?id=%s',
            'saved': 'data/hn_favorite.json',
            # 0 to get all this type pages
            # 'max_page': 0,
            'max_page': 10,
            'login': True,
            },
        )


max_retry = 3
max_items_per_cat = 3000
skip_cat_when_large_then = 1100

reddit_json_file = 'data/reddit.json'
reddit_csv_file = 'data/reddit.csv'

reddit_urls = [
      ('life', 
          ('https://www.reddit.com/r/Life/', 
              'https://www.reddit.com/r/Life/top/')),
      ('literature', 
          ('https://www.reddit.com/r/literature/', 
                  'https://www.reddit.com/r/literature/top/')),
      ('painting', 
          ('https://www.reddit.com/r/painting/', 
                  'https://www.reddit.com/r/painting/top/')),
      # failed
      #('music', 
      #    ('https://www.reddit.com/r/music/', 
      #            'https://www.reddit.com/r/music/top/')),
      ('movie', 
              ('https://www.reddit.com/r/movies/', 
                  'https://www.reddit.com/r/movies/top/')),
      ('scifi', 
          ('https://www.reddit.com/r/scifi/', 
              'https://www.reddit.com/r/scifi/top/')),
      ('cyberpunk', 
          ('https://www.reddit.com/r/Cyberpunk/', 
              'https://www.reddit.com/r/Cyberpunk/top/')),
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
       ('hacking', 
            ('https://www.reddit.com/r/hacking/', 
                'https://www.reddit.com/r/hacking/top/')),
       ('security', 
           ('https://www.reddit.com/r/security/', 
                'https://www.reddit.com/r/security/top/')),
       ('cyber_security', 
           ('https://www.reddit.com/r/cybersecurity/', 
                'https://www.reddit.com/r/cybersecurity/top/')),
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

        ('space', 
            ('https://www.reddit.com/r/space/', 
                'https://www.reddit.com/r/space/top/')),
        ('physics', 
            ('https://www.reddit.com/r/Physics/', 
                'https://www.reddit.com/r/Physics/top/')),
        ('math', 
            ('https://www.reddit.com/r/math/', 
                'https://www.reddit.com/r/math/top/')),
        ('philosophy', 
            ('https://www.reddit.com/r/philosophy/', 
                'https://www.reddit.com/r/philosophy/top/')),
        ('logic', 
            ('https://www.reddit.com/r/logic/', 
                'https://www.reddit.com/r/logic/top/')),
        ('crypto', 
            ('https://www.reddit.com/r/crypto/', 
                'https://www.reddit.com/r/crypto/top/')),
        ('algorithm', 
            ('https://www.reddit.com/r/algorithms/', 
                'https://www.reddit.com/r/algorithms/top/')),
        ('tiny_code', 
            ('https://www.reddit.com/r/tinycode/', 
                'https://www.reddit.com/r/tinycode/top/')),

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
      # failed
      # ('causality', 
      #     ('https://www.reddit.com/r/causality/', 
      #         'https://www.reddit.com/r/causality/top/')),

        ('i2p', 
            ('https://www.reddit.com/r/i2p/', 
                'https://www.reddit.com/r/i2p/top/')),
        ('tor', 
            ('https://www.reddit.com/r/TOR/', 
                'https://www.reddit.com/r/TOR/top/')),
      # failed
      # ('p2p', 
      #     ('https://www.reddit.com/r/P2P/', 
      #         'https://www.reddit.com/r/P2P/top/')),
        ('decentralization', 
                ('https://www.reddit.com/r/decentralization/',
                    'https://www.reddit.com/r/decentralization/top/', 
                    'https://www.reddit.com/r/Rad_Decentralization/top/',
                    'https://www.reddit.com/r/DistributedComputing/top/')),
      # failed
      # ('privacy', 
      #     ('https://www.reddit.com/r/Privacy/', 
      #         'https://www.reddit.com/r/Privacy/top/')),
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

reddit_headers = {
            'Host': 'www.reddit.com',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            # this have to ungzip
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cookie': '',
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'Trailers',
            }

reddit_skip_cat = ['painting']
reddit_skip_domain = ['youtu.be', 'youtube.com', 'imgur.com']

