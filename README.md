<h1 align="center">Hacker News on Console(CHN)</h1>

<p align="center">
A text-based interface (TUI) to view and interact with Hacker News from your Console.<br>
With auto classifer and recommender with relate to your upvotes and favorites.<br>
UI code is in reactjs style, easy and familiar for many developer who like reactjs.
</p>

<p align="center">
<img alt="title image" src="data/title-image.png"/>
</p>


## Table of Contents

* [NOTICE](#notice)  
* [Features](#features)  
* [Installation](#installation)  
* [Usage](#usage)  
* [Settings](#settings)
* [TODO](#todo)  
* [Train your own classifer](#train)  
* [License](#license)  


## Notice
CHN tested in Ubuntu in its default terminal, ONLY work with python3.6.7, and maybe python3+, macOS/windows and other OS did not tested.

CHN is still in early stage, may have many bugs and performance problems, but it is aslo useful now.

Classifer just have around 71% accuracy at present, as it is trained by classify just post titles for 34 categories,
and the data is not so many, has only around 150000 samples, quite imbalanced.
you can train your own classifer, more details about the data/classifer and train method see [Train your own classifer](#train)


## Features
* login to HN and vote/favorite post
* browser all HN list pages include your submitted/voted/favorite page
* use classifer or search to filter different page posts
* auto recommend posts for your interest

create comment/post and view detail did not implement, they are in [TODO](#todo)


## Installation
git clone https://github.com/ghosthamlet/CHN.git

cd CHN

pip3 install -r requirements.txt


## Usage
RUN:

python3 ui.py

THAT's All.


SHORTCUTS:

    h: show/close help screen

    s: goto search keyword, use space to seperate multi keywords

    t: goto select page type, or go back to posts

    v: upvote current post(NOTE: you have to view/load upvoted page first)

    o: favorite current post(NOTE: you have to view/load favorite page first)

    r: refresh posts

    c: open comment page

    enter: open link page

    ctrl c: quit


NOTICE:

    * login is safe, just cookies will save on your computer, 
       accounts will not save, not send to any servers

    * login may FAILED! when you try many times wrong username/password, your ip maybe locked by HN, 
       and it will use google reCAPTCHA to verify your login, you have to wait HN to remove reCAPTCHA to login CHN again

    * use arrows to navigate

    * sometimes after loading new page, ui maybe frozen, hit t to activate it

    * load submitted/upvoted/favorite pages maybe very slow first time if you have many data, 
       but after first load it will be fast
 

## Train
### About the data 
### About the classifer
### Train your own classifer
1. change reddit crawl settings in config.py, crawl subreddits posts by run crawler.py, you can use exists data/reddit.csv and skip this step
2. train in Train.ipynb, read some classify accuracy comments in it 
3. change hn_classifer_model in config.py with saved model of the previous step 


## Settings
see config.py


## TODO
* use hyperparameter-hunter to manage machine learning experiments
* optimize classifer accuracy by crawl and classify posts body not just
  title, and use deep transfer learning(maybe fine tuning BERT) to classify
* optimize recommender performance by compare posts body, aslo optimize its
  speed, it is rather slow now, maybe remove spacy and use raw word2vec
* optimize app ui performance, add more progress reminder
* updating guest pages will update all data of that page now,
  change it to incremental updates like the user only pages
* optimize react speed, let render just update itself component, not all components
* refactor react api/code to more conform to reactjs, and extract it to independent pip library
* add vim like shortcuts
* add comment/post detail page, search/sort post comments, and create comment/post functions
* add chart/graph page to show cats/keywords of submitted/upvoted/favorite stats along time
* make the latest/hot/recommend page real time

## License
This project is distributed under the [MIT](LICENSE) license.
