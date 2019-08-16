#coding=utf8

import re

import urwid

from chn import HnData, HnCrawler, HnAnalyze

from react import React, Component 


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


class HnConsole(Component):
    def __init__(self):
        self.hn_data = HnData()
        self.crawle  = HnCrawler()
        self.analyze = HnAnalyze()

        self.state = dict(
                current_page_type='hot',
                current_cat='All',
                username='',
                password='',
                is_login=False,
                posts={},
        )

        self.init()

    def init(self, crawler_new=False):
        if crawler_new:
            self.crawle.save('/', self.state['current_page_type'])
        
        self.load_posts(self.state['current_page_type'])

    def render_header(self):
        posts = {}
        for _, p in self.get_posts(self.state['current_page_type']).items():
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

    def load_posts(self, page_type):
        self.hn_data.load_posts(page_type)
        posts = self.hn_data.all_posts[page_type]
        self.analyze.assoc_cat(posts)

        self.set_state({'all_posts': {page_type: posts}})

    def get_posts(self, page_type):
        return self.state['all_posts'][page_type]

    def render_posts(self, posts):
        choices = []
        posts_sorted = sorted(posts.items(), key=lambda x: x[1]['rank'])

        for url, p in posts_sorted:
            choices.append('%s. [%s] %s' % (p['rank'], p['cat'], p['title']))
        ls_el = urwid.Padding(create_list(choices), left=1, right=1)
        return ls_el

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
        self.set_state({'current_cat': key})

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
        self.set_state({'is_login': True})

    def render_page_btns(self):
        body = []
        choices = []

        for page_alias, meta in self.hn_data.pages.items():
            if not self.state['is_login'] and meta['login']:
                continue

            button = urwid.Button(page_alias)
            urwid.connect_signal(button, 'click', lambda el, choice: self.on_select_page(choice), page_alias)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))

        focus_el = urwid.SimpleFocusListWalker(body)
        # have to wrap Columns/GridFlow in ListBox, or Pile can't work
        return urwid.ListBox([urwid.Columns(focus_el)])

    def on_select_page(self, page_alias):
        pass

    def render(self):
        if self.state['is_login']:
            login_el = urwid.ListBox([urwid.Text(self.state['username'])])
        else:
            login_el = self.render_login_form()
        pages_el = self.render_page_btns()
        header_el = self.render_header()
        posts = {url:p for url, p in self.get_posts(self.state['current_page_type']).items()
                 if p['cat'] == self.state['current_cat'] or self.state['current_cat'] == 'All'}
        ls_el = self.render_posts(posts)

        # page = urwid.Frame(ls_el, header_el, focus_part='header')
        return [
            (login_el, ('weight', 1)), 
            (pages_el, ('weight', 1)), 
            (header_el, ('weight', 2)),
            (ls_el, ('weight', 8))
        ]


if __name__ == '__main__':
    from train import *
    React.render(HnConsole())

