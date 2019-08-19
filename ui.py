#coding=utf8

import sys
import re
import logging
import threading

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
    button_right = urwid.Text('')


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
    signals = ['focus_search', 'trigger_help']

    def keypress(self, size, key):
        super().keypress(size, key)

        login_pos = 0
        focus = self.focus_position
        is_focus_login = focus == login_pos

        if not is_focus_login:
            if key == 's':
                self.focus_position = 0
                self._emit('focus_search')
            elif key == 'h':
                self._emit('trigger_help')


def create_list(page_type, choices):
    body = [urwid.Text(page_type), urwid.Divider()]
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
        return urwid.ListBox([urwid.Columns(focus_el)])

    def on_click_login(self):
        username = self.username_el.edit_text.strip()
        password = self.password_el.edit_text.strip()

        if not username or not password:
            return

        self.props['on_login']()

    def render_search_form(self):
        self.search_el = urwid.Edit('Keyword: ', edit_text=self.props['search_keyword'])
        submit_search_el = urwid.Button('Search')
        urwid.connect_signal(submit_search_el, 'click', lambda button: self.on_click_search())
        return self.search_el, submit_search_el

    def on_click_search(self):
        keyword = self.search_el.edit_text.strip().lower()
        self.props['on_search'](keyword)

    def render(self):
        if self.props['is_login']:
            login_el = urwid.ListBox([urwid.Columns([urwid.Text(self.props['username'] or 'Logged'), *self.render_search_form()])])
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

            button = urwid.Button(page_type)
            urwid.connect_signal(button, 'click', lambda el, choice: self.on_select_page(choice), page_type)
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

        return urwid.Padding(create_list(self.props['page_type'], posts_sorted), left=1, right=1)


class Help(Component):
    TEXT = '''
    Help:
        shortcuts:
        h: show/close this screen
        s: goto input search keyword
    '''
    def render(self):
        return urwid.ListBox([urwid.Text(Help.Text)])


# TODO: add translation option for titles
class App(Component):
    def __init__(self, **props):
        super().__init__(**props)

        self.root_el = self.props['root_el']
        self.login_el = None

        self.hn_data = HnData()
        self.crawle  = HnCrawler()
        self.analyze = HnAnalyze()

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
        )

        urwid.connect_signal(self.root_el, 'focus_search', lambda el: self.focus_search())
        urwid.connect_signal(self.root_el, 'trigger_help', lambda el: self.trigger_help())

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
        self.set_state({'current_page_type': page_type, 'loading': True})

        def bgf():
            page_meta = self.hn_data.pages[page_type]
            url = page_meta['url'] % self.state['username'] if page_meta['login'] else page_meta['url']
            logger.info('select page: %s' % url)
            self.crawle.save(url, page_type)
            logger.info('page saved: %s' % url)
            self.load_posts(page_type)

        t = threading.Thread(target=bgf)
        t.start()
        t.join()

    def focus_search(self):
        if self.state['loading']:
            return

        self.root_el.focus_position = 0
        if self.state['is_login']:
            self.login_el.contents()[0][0].focus_position = 1
        else:
            self.login_el.contents()[0][0].focus_position = 3

    def trigger_help(self):
        if self.state['loading']:
            return

        self.set_state({'show_help': not self.state['show_help']})

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
        posts = self.get_posts(self.state['current_page_type'])
        if search_keyword:
            posts_searched = {url:p for url, p in posts.items()
                              if search_keyword in p['title'].lower() 
                              or search_keyword in p['cat'].lower()
                              or search_keyword in p['auther'].lower()}
        else:
            posts_searched = posts
        posts_filtered = {url:p for url, p in posts_searched.items()
                          if p['cat'] == current_cat or current_cat == 'All'}

        self.login_el = React.create_element(LoginForm, 'login', 
                is_login=is_login, on_login=self.on_login, 
                username=self.state['username'], password=self.state['password'],
                set_username=self.set_username, set_password=self.set_password,
                search_keyword=self.state['search_keyword'], on_search=self.on_search)
        page_btns_el = React.create_element(PageBtns, 'page_btns', 
                is_login=is_login, pages=self.hn_data.pages,
                on_select_page=self.on_select_page)
        header_el = React.create_element(Header, 'header', posts=posts_searched, on_select_cat=self.on_select_cat)
        if self.state['loading']:
            posts_el = urwid.ListBox([urwid.Text('Loading...')])
        else:
            posts_el = React.create_element(Posts, 'posts',
                    posts=posts_filtered, page_type=self.state['current_page_type'])

        return [
            (self.login_el, ('weight', .5)), 
            (page_btns_el, ('weight', .5)), 
            (header_el, ('weight', .5)),
            (posts_el, ('weight', 10))
        ]


if __name__ == '__main__':
    from train import *
    root_el = HnPile([])
    ReactConsole.render(React.create_element(App, 'app', root_el=root_el, return_instance=True), root_el)

