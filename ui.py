#coding=utf8

import sys
import re
import logging
import threading
import time

import urwid

from chn import HnData, HnCrawler, HnAnalyze

from react import React, ReactConsole, Component 


logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger()

fileHandler = logging.FileHandler("{0}/{1}.log".format('data', 'ui'))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

# consoleHandler = logging.StreamHandler()
# consoleHandler.setFormatter(logFormatter)
# logger.addHandler(consoleHandler)
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
    button_right = urwid.Text('|')


class HnListItem(urwid.Button):
    button_left = urwid.Text('')
    button_right = urwid.Text('')


class HnEdit(urwid.Edit):
    signals = ['change', 'postchange', 'click']

    def keypress(self, size, key):
        super().keypress(size, key)

        if key == 'enter' and not self.multiline:
            self._emit('click')
        elif key == 'tab' and not self.allow_tab:
            # goto next selectable
            return key
        return key


class HnPile(urwid.Pile):
    signals = ['focus_search', 'trigger_help', 'trigger_focus_top']

    def keypress(self, size, key):
        super().keypress(size, key)

        if key == 's':
            self._emit('focus_search')
        elif key == 'h':
            self._emit('trigger_help')
        elif key == 't':
            self._emit('trigger_focus_top')


def create_list(page_type, choices):
    body = [urwid.Text(page_type, align='center'), urwid.Divider()]
    for url, p in choices:
        title = '%s. [%s] %s' % (p['rank'], p['cat'], p['title'])
        button = HnListItem(title)
        urwid.connect_signal(button, 'click', list_item_chosen, url)
        infos = urwid.Columns([
            urwid.Text('%s points' % p['score']),
            urwid.Text('by %s' % p['auther']),
            urwid.Text('%s ' % p['age']),
            urwid.Text('%s comments' % p['comment_cnt']),
            ])
        pile = urwid.Pile([button, infos])
        body.append(urwid.AttrMap(pile, None, focus_map='reversed'))
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
        self.username_el = None
        self.password_el = None
        self.search_el = None

    def render_login_form(self):
        self.username_el = urwid.Edit('Username: ', edit_text=self.props['username'])
        self.password_el = urwid.Edit('Password: ', edit_text=self.props['password'])
        submit_el = urwid.Button('Submit')

        urwid.connect_signal(self.username_el, 'change', 
                lambda el, s: self.props['set_username'](s.strip()))
        urwid.connect_signal(self.password_el, 'change', 
                lambda el, s: self.props['set_password'](s.strip()))
        urwid.connect_signal(submit_el, 'click', lambda button: self.on_click_login())

        focus_el = urwid.SimpleFocusListWalker([self.username_el, self.password_el, 
            submit_el, *self.render_search_form()])
        # have to wrap Columns/GridFlow in ListBox, or Pile can't work
        return urwid.ListBox([urwid.Columns(focus_el), urwid.Divider('-')])

    def on_click_login(self):
        username = self.username_el.edit_text.strip()
        password = self.password_el.edit_text.strip()

        if not username or not password:
            return

        self.props['on_login']()

    def render_search_form(self):
        self.search_el = HnEdit('Keyword: ', edit_text=self.props['search_keyword'])

        urwid.connect_signal(self.search_el, 'click', lambda button: self.on_click_search())
        return self.search_el,

    def on_click_search(self):
        keyword = self.search_el.edit_text.strip().lower()
        self.props['on_search'](keyword)

    def render(self):
        if self.props['is_login']:
            login_el = urwid.ListBox([
                urwid.Columns([urwid.Text(self.props['username'] or 'Logged'), *self.render_search_form()]), 
                urwid.Divider('-')])
        else:
            login_el = self.render_login_form()

        return login_el


class PageBtns(Component):
    def on_select_page(self, page_type):
        self.props['on_select_page'](page_type)

    def render(self):
        body = []
        choices = []

        for page_type, meta in self.props['pages'].items():
            if not self.props['is_login'] and meta['login']:
                continue

            button = HnButton(page_type)
            urwid.connect_signal(button, 'click', lambda el, choice: self.on_select_page(choice), page_type)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))

        focus_el = urwid.SimpleFocusListWalker(body)
        # have to wrap Columns/GridFlow in ListBox, or Pile can't work
        return urwid.ListBox([urwid.Columns(focus_el), urwid.Divider('-')])


class Header(Component):
    def render_menu(self, choices):
        body = []
        choices = ['All', *choices]
        for c in choices:
            button = HnButton(c)
            urwid.connect_signal(button, 'click', lambda el, choice: self.on_select_cat(choice), c)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))

        focus_el = urwid.SimpleFocusListWalker(body)
        # have to wrap Columns/GridFlow in ListBox, or Pile can't work
        # return urwid.ListBox([urwid.Columns(focus_el)])
        return urwid.ListBox(focus_el)

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
        for cat, cnt in posts:
            if cnt > 0:
                choices.append('%s(%s)' % (cat, cnt))
        header_el = self.render_menu(choices)
        return header_el


class Posts(Component):
    def render(self):
        choices = []
        posts_sorted = sorted(self.props['posts'].items(), key=lambda x: x[1]['rank'])

        return urwid.Padding(create_list(self.props['page_type'], posts_sorted), left=1, right=1)


class Help(Component):
    TEXT = '''
    Help:
        h: show/close this screen
        s: goto search keyword, use space to seperate multi keywords
        t: goto select page type, or go back to posts
    '''
    def render(self):
        return urwid.ListBox([urwid.Text(Help.TEXT)])


# TODO: add translation option for titles
class App(Component):
    def __init__(self, **props):
        super().__init__(**props)

        self.root_el = self.props['root_el']
        self.login_el = None

        self.hn_data = HnData()
        self.crawle  = HnCrawler()
        self.analyze = HnAnalyze()
        self.loading_thread = None

        self.state = dict(
                current_page_type='hot',
                current_cat='All',
                search_keyword='',
                username='',
                password='',
                is_login=not not self.crawle.cookies,
                all_posts={},
                show_help=False,
                loading=True,
                loading_content='',
        )

        urwid.connect_signal(self.root_el, 'focus_search', lambda el: self.focus_search())
        urwid.connect_signal(self.root_el, 'trigger_help', lambda el: self.trigger_help())
        urwid.connect_signal(self.root_el, 'trigger_focus_top', lambda el: self.trigger_focus_top())

    def init(self, crawler_new=False):
        current_page_type = self.state['current_page_type']
        if crawler_new:
            self.crawle.save(self.hn_data.pages[current_page_type]['url'], current_page_type)
        
        self.load_posts(current_page_type)

    def load_posts(self, page_type):
        self.hn_data.load_posts(page_type)
        posts = self.hn_data.all_posts[page_type]
        self.analyze.assoc_cat(posts)
        logger.info('loaded posts: %s' % len(posts))

        self.set_state({'all_posts': {page_type: posts}, 'loading': False})

    def get_posts(self, page_type):
        return self.state['all_posts'].get(page_type, {})

    def on_login(self):
        self.crawle.login(self.state['username'], self.state['password'])
        self.set_state({'is_login': True})

    def on_search(self, keyword):
        self.set_state({'search_keyword': keyword})

    def on_select_cat(self, cat):
        self.set_state({'current_cat': cat})

    def on_select_page(self, page_type):
        self.set_state({'loading': True, 'loading_content': page_type})

        def bgf():
            page_meta = self.hn_data.pages[page_type]
            url = page_meta['url'] % self.state['username'] if page_meta['login'] else page_meta['url']
            logger.info('select page: %s' % url)
            self.crawle.save(url, page_type)
            logger.info('page saved: %s' % url)
            self.load_posts(page_type)
            self.set_state({'current_page_type': page_type})

        self.loading_thread = threading.Thread(target=bgf)
        self.loading_thread.start()
        # FIXME: join will frozen ui, and can't show loading progress,
        #        but then ui have to update while manual move cursor without join()
        # self.loading_thread.join()

    def focus_search(self):
        if self.state['loading'] or self.state['show_help'] or self.is_focus_login():
            return

        self.focus_login()
        if self.state['is_login']:
            self.login_el.contents()[0][0].focus_position = 1
        else:
            self.login_el.contents()[0][0].focus_position = 3

    def trigger_help(self):
        if self.state['loading'] or self.is_focus_login():
            return

        self.set_state({'show_help': not self.state['show_help']})
        if not self.state['show_help']:
            self.root_el.focus_position = 2

    def trigger_focus_top(self):
        if self.state['loading'] or self.state['show_help'] or self.is_focus_login():
            return

        if self.root_el.focus_position != 2:
            self.root_el.focus_position = 2
        else:
            self.root_el.focus_position = len(self.root_el.contents) - 1

    def is_focus_login(self):
        return self.root_el.focus_position == 1 and len(self.root_el.contents) > 1

    def focus_login(self):
        self.root_el.focus_position = 1

    def set_username(self, s):
        self.set_state({'username': s}, disable_render=True)

    def set_password(self, s):
        self.set_state({'password': s}, disable_render=True)

    def component_did_mount(self):
        self.init()

    def render(self):
        if self.state['show_help']:
            return [(React.create_element(Help, 'help'), ('weight', 10))]

        is_login = self.state['is_login']
        current_cat = self.state['current_cat']
        search_keyword = self.state['search_keyword']
        current_page_type = self.state['current_page_type']
        posts = self.get_posts(current_page_type)
        if search_keyword:
            ks = search_keyword.split(' ')
            fn = lambda t: any(map(lambda k: k and k in t, ks))
            posts_searched = {url:p for url, p in posts.items()
                              if fn(p['title'].lower())
                              or fn(p['cat'].lower())
                              or fn(p['auther'].lower())}
        else:
            posts_searched = posts
        posts_filtered = {url:p for url, p in posts_searched.items()
                          if p['cat'] == current_cat or current_cat == 'All'}

        loading_el = urwid.ListBox([urwid.Text('CHN', align='center')])
        loading_el = urwid.AttrMap(loading_el, 'reversed')
        if self.state['loading']:
            loading_el = urwid.ListBox([urwid.Text('Loading %s...' % self.state['loading_content'], align='center')])
            loading_el = urwid.AttrMap(loading_el, 'loading')

        self.login_el = React.create_element(LoginForm, 'login', 
                is_login=is_login, on_login=self.on_login, 
                username=self.state['username'], password=self.state['password'],
                set_username=self.set_username, set_password=self.set_password,
                search_keyword=self.state['search_keyword'], on_search=self.on_search)
        page_btns_el = React.create_element(PageBtns, 'page_btns', 
                is_login=is_login, pages=self.hn_data.pages,
                on_select_page=self.on_select_page)
        header_el = React.create_element(Header, 'header', posts=posts_searched, on_select_cat=self.on_select_cat)
        posts_el = React.create_element(Posts, 'posts',
                posts=posts_filtered, page_type=current_page_type)
        # body_el = urwid.ListBox([urwid.Columns([header_el, posts_el])])
        body_el = urwid.Columns([('weight', 2, header_el), ('weight', 10, posts_el)])

        return [
            (loading_el, ('weight', .2)), 
            (self.login_el, ('weight', .5)), 
            (page_btns_el, ('weight', .5)), 
            # (header_el, ('weight', .5)),
            # (posts_el, ('weight', 10))
            (body_el, ('weight', 10))
        ]


if __name__ == '__main__':
    from train import *
    root_el = HnPile([])
    ReactConsole.render(React.create_element(App, 'app', root_el=root_el, return_instance=True), root_el)

