#coding=utf8

import sys
import re
import logging

import urwid

from chn import HnData, HnCrawler, HnAnalyze

from react import React, Component 


logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger()

fileHandler = logging.FileHandler("{0}/{1}.log".format('data', 'ui'))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
logger.setLevel(logging.INFO)
# logger.info('')

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
#     handlers=[
#         logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
#         logging.StreamHandler()
#     ])


class HnButton(urwid.Button):
    button_left = urwid.Text('')
    button_right = urwid.Text('')


class HnListItem(urwid.Button):
    button_left = urwid.Text('')
    button_right = urwid.Text('')


def create_list(choices):
    body = [urwid.Text('test'), urwid.Divider()]
    for c in choices:
        button = HnListItem(c)
        urwid.connect_signal(button, 'click', list_item_chosen, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))


def list_item_chosen(button, choice):
    response = urwid.Text([u'You chose ', choice, u'\n'])
    done = urwid.Button(u'Ok')
    urwid.connect_signal(done, 'click', exit_program)
    main.original_widget = urwid.Filler(urwid.Pile([response,
        urwid.AttrMap(done, None, focus_map='reversed')]))


def exit_program(button):
    raise urwid.ExitMainLoop()


class LoginForm(Component):
    def __init__(self, **props):
        super().__init__(**props)

        self.state = dict(
                username='',
                password='',
        )

    def render_login_form(self):
        username_el = urwid.Edit('Username: ')
        password_el = urwid.Edit('Password: ')
        submit_el = urwid.Button('Submit')
        urwid.connect_signal(username_el, 'change', 
                lambda el, s: self.set_state({'username': s.strip()}, disable_render=True))
        urwid.connect_signal(password_el, 'change', 
                lambda el, s: self.set_state({'password': s.strip()}, disable_render=True))
        urwid.connect_signal(submit_el , 'click', lambda button: self.on_click_login())

        focus_el = urwid.SimpleFocusListWalker([username_el, password_el, submit_el])
        # have to wrap Columns/GridFlow in ListBox, or Pile can't work
        return urwid.ListBox([urwid.Columns(focus_el)])

    def on_click_login(self):
        if not self.state['username'] or not self.state['password']:
            return

        # self.crawle.login(self.state['username'], self.state['password'])
        self.props['on_login']()

    def render(self):
        if self.props['is_login']:
            login_el = urwid.ListBox([urwid.Text(self.state['username'])])
        else:
            login_el = self.render_login_form()

        return login_el


class PageBtns(Component):
    def on_select_page(self, page_alias):
        pass

    def render(self):
        body = []
        choices = []

        for page_alias, meta in self.props['pages'].items():
            if not self.props['is_login'] and meta['login']:
                continue

            button = urwid.Button(page_alias)
            urwid.connect_signal(button, 'click', lambda el, choice: self.on_select_page(choice), page_alias)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))

        focus_el = urwid.SimpleFocusListWalker(body)
        # have to wrap Columns/GridFlow in ListBox, or Pile can't work
        return urwid.ListBox([urwid.Columns(focus_el)])


class Header(Component):
    def render_menu(self, choices):
        body = []
        choices = ['All', *choices]
        for c in choices:
            button = urwid.Button(c)
            urwid.connect_signal(button, 'click', lambda el, choice: self.on_select_cat(choice), c)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))

        focus_el = urwid.SimpleFocusListWalker(body)
        # have to wrap Columns/GridFlow in ListBox, or Pile can't work
        return urwid.ListBox([urwid.Columns(focus_el)])

    def on_select_cat(self, choice):
        key = re.sub('\(.+\)', '', choice)
        self.props['on_select_cat'](key)

    def render(self):
        posts = {}
        for _, p in self.props['posts'].items():
            if p['cat'] not in posts:
                posts[p['cat']] = 1
            else:
                posts[p['cat']] += 1
        posts = sorted(posts.items(), key=lambda x: x[1], reverse=True)

        choices = []
        # for cat in self.analyze.model.classes_[:6]:
        for cat, cnt in posts[:6]:
            if cnt > 0:
                choices.append('%s(%s)' % (cat, cnt))
        header_el = urwid.Padding(self.render_menu(choices), left=1, right=1)
        return header_el


class Posts(Component):
    def render(self):
        choices = []
        posts_sorted = sorted(self.props['posts'].items(), key=lambda x: x[1]['rank'])

        for url, p in posts_sorted:
            choices.append('%s. [%s] %s' % (p['rank'], p['cat'], p['title']))
        return urwid.Padding(create_list(choices), left=1, right=1)


class App(Component):
    def __init__(self, **props):
        super().__init__(**props)

        self.hn_data = HnData()
        self.crawle  = HnCrawler()
        self.analyze = HnAnalyze()

        self.state = dict(
                current_page_type='hot',
                current_cat='All',
                is_login=False,
                posts={},
        )

        self.init()

    def init(self, crawler_new=False):
        if crawler_new:
            self.crawle.save('/', self.state['current_page_type'])
        
        self.load_posts(self.state['current_page_type'])

    def load_posts(self, page_type):
        self.hn_data.load_posts(page_type)
        posts = self.hn_data.all_posts[page_type]
        self.analyze.assoc_cat(posts)

        self.set_state({'all_posts': {page_type: posts}})

    def get_posts(self, page_type):
        return self.state['all_posts'][page_type]

    def on_login(self):
        self.set_state({'is_login': True})

    def on_select_cat(self, cat):
        self.set_state({'current_cat': cat})

    def render(self):
        is_login = self.state['is_login']
        current_cat = self.state['current_cat']
        posts = self.get_posts(self.state['current_page_type'])
        posts_filtered = {url:p for url, p in posts.items()
                          if p['cat'] == current_cat or current_cat == 'All'}

        login_el = LoginForm.factory('login', is_login=is_login, on_login=self.on_login).render()
        page_btns_el = PageBtns.factory('page_btns', is_login=is_login, pages=self.hn_data.pages).render()
        header_el = Header.factory('header', posts=posts, on_select_cat=self.on_select_cat).render()
        posts_el = Posts.factory('posts', posts=posts_filtered).render()

        # page = urwid.Frame(posts_el, header_el, focus_part='header')
        return [
            (login_el, ('weight', 1)), 
            (page_btns_el, ('weight', 1)), 
            (header_el, ('weight', 2)),
            (posts_el, ('weight', 8))
        ]


if __name__ == '__main__':
    from train import *
    React.render(App())

