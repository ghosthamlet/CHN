#coding=utf8

import sys
import re
import logging
import threading
import time
import webbrowser

import urwid

from chn import HnData, HnClient, HnAnalyze

from react import React, ReactConsole, Component 
import utils


logger = utils.get_logger()


class HnButton(urwid.Button):
    button_left = urwid.Text('')
    button_right = urwid.Text('|')


class HnListItem(urwid.Button):
    button_left = urwid.Text('')
    button_right = urwid.Text('')

    def set_identity(self, identity):
        self.identity = identity


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
    # upvote favorite just can do in posts not by incremental download
    # as the the actions maybe used time based token
    signals = ['focus_search', 'trigger_help', 'trigger_focus_top',
                'trigger_upvote', 'trigger_favorite', 'refresh']

    def keypress(self, size, key):
        super().keypress(size, key)

        if key == 's':
            self._emit('focus_search')
        elif key == 'h':
            self._emit('trigger_help')
        elif key == 't':
            self._emit('trigger_focus_top')
        elif key == 'r':
            self._emit('refresh')
        elif key == 'v':
            self._emit('trigger_upvote')
        elif key == 'o':
            self._emit('trigger_favorite')


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


class SideBar(Component):
    def render_menu(self, choices):
        body = []
        sortes = [
                'default',
                'score',
                'comment'
                ]
        body.append(urwid.Text('Sort:'))
        for c in sortes:
            button = HnButton(c)
            urwid.connect_signal(button, 'click', lambda el, choice: self.on_select_sort(choice), c)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))

        choices = [
                'all', 
                *choices
        ]

        body.append(urwid.Text(''))
        body.append(urwid.Text('Cat:'))
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

    def on_select_sort(self, choice):
        self.props['on_select_sort'](choice)

    def render(self):
        posts = {}
        for p in self.props['posts']:
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
        return self.render_menu(choices)


class Posts(Component):
    def create_list(self, page_type, choices):
        upvoteds = [utils.get_post_identity(v) for v in self.props['posts_upvoted']]
        favorites = [utils.get_post_identity(v) for v in self.props['posts_favorite']]
        body = [urwid.Text(page_type, align='center'), urwid.Divider()]

        for i, p in enumerate(choices):
            identity = utils.get_post_identity(p)
            is_upvoted = identity  in upvoteds
            is_favorite = identity in favorites
            title_el = HnListItem(p['title'])
            title_el.set_identity(identity)
            upvote_el = urwid.Text([
                ('subtext', '^') if not is_upvoted else ' ', 
                ('highlight', '*') if is_favorite else ' '
                ])
            header_el = urwid.Columns([
                # ('pack', urwid.Text([('subtext', '%s. ' % p['rank']), ('cat', '[%s]' % p['cat'])])),
                ('pack', urwid.Text(('subtext', '%s. ' % i))),
                # XXX: button have to use weight
                # ('weight', .2, upvote_el),
                ('pack', upvote_el),
                ('pack', urwid.Text(('cat', '[%s]' % p['cat']))),
                ('weight', 10, title_el),
                ('pack', urwid.Text(('subtext', p['site']))),
            ])
            urwid.connect_signal(title_el, 'click', self.on_click_title, p['url'])

            subtext_el = urwid.Columns([
                urwid.Text(' '),
                urwid.Text('%s points' % p['score']),
                urwid.Text('by %s' % p['auther']),
                urwid.Text('%s ' % p['age']),
                urwid.Text('%s comments' % p['comment_cnt']),
                ])

            pile_el = urwid.Pile([
                header_el, 
                urwid.AttrMap(subtext_el, 'subtext')
            ])
            body.append(urwid.AttrMap(pile_el, None, focus_map='reversed'))
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def on_click_title(self, button, url):
        url = url if url[:4] == 'http' else '%s/%s' % (config.hn_domain, url)
        webbrowser.open_new_tab(url)

    def render(self):
        return urwid.Padding(self.create_list(self.props['page_type'], self.props['posts']), left=1, right=1)


class Help(Component):
    TEXT = '''
    Help:
        h: show/close this screen
        s: goto search keyword, use space to seperate multi keywords
        t: goto select page type, or go back to posts
        r: refresh posts
        v: upvote current post(NOTE: you have to view/load upvoted page first)
        o: favorite current post(NOTE: you have to view/load favorite page first)
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
        self.client  = HnClient()
        self.analyze = HnAnalyze()

        self.state = dict(
                current_page_type='hot',
                current_cat='all',
                current_sort='default',
                current_sort_dir='desc',
                search_keyword='',
                username=self.client.get_username(),
                password='',
                is_login=not not self.client.cookies,
                all_posts={},
                show_help=False,
                loading=True,
                loading_content='',
        )

        urwid.connect_signal(self.root_el, 'focus_search', lambda el: self.focus_search())
        urwid.connect_signal(self.root_el, 'trigger_help', lambda el: self.trigger_help())
        urwid.connect_signal(self.root_el, 'trigger_focus_top', lambda el: self.trigger_focus_top())
        urwid.connect_signal(self.root_el, 'trigger_upvote', lambda el: self.trigger_upvote())
        urwid.connect_signal(self.root_el, 'trigger_favorite', lambda el: self.trigger_favorite())
        urwid.connect_signal(self.root_el, 'refresh', lambda el: self.refresh())

    def init(self, refresh=True):
        current_page_type = self.state['current_page_type']
        self.client.download_posts(self.hn_data.pages[current_page_type]['url'], 
                current_page_type, refresh=refresh)
        
        self.load_posts('upvoted')
        self.load_posts('favorite')
        self.load_posts(current_page_type)

    def load_posts(self, page_type):
        self.hn_data.load_posts(page_type)
        posts = self.hn_data.all_posts[page_type]
        self.analyze.assoc_cat(posts)
        logger.info('loaded posts: %s' % len(posts))

        all_posts = {**self.state['all_posts'], page_type: posts}
        self.set_state({'all_posts': all_posts, 'loading': False})

    def get_posts(self, page_type):
        return self.state['all_posts'].get(page_type, [])

    def on_login(self):
        self.client.login(self.state['username'], self.state['password'])
        self.set_state({'is_login': True})

    def on_search(self, keyword):
        self.set_state({'search_keyword': keyword})

    def on_select_cat(self, cat):
        self.set_state({'current_cat': cat})

    def on_select_sort(self, sort):
        sort_dir = 'asc' if self.state['current_sort_dir'] == 'desc' else 'desc'
        self.set_state({'current_sort': sort, 'current_sort_dir': sort_dir})

    # FIXME: event binded and run multi times parallel, see data/ui.log
    def on_select_page(self, page_type):
        if self.state['loading']:
            return

        self.set_state({'loading': True, 'loading_content': page_type})

        def bgf():
            self.download_posts(page_type)
            self.load_posts(page_type)
            # XXX: load_posts already change loading, don't set loading again, or ui will forzen
            # self.set_state({'loading': False, 'current_page_type': page_type})
            self.set_state({'current_page_type': page_type})

        threading.Thread(target=bgf).start()
        # join will frozen ui, and can't show loading progress,
        # let update_screen in set_state to do async update
        # self.loading_thread.join()

    def download_posts(self, page_type):
        page_meta = self.hn_data.pages[page_type]
        url = page_meta['url'] % self.state['username'] if page_meta['login'] else page_meta['url']
        logger.info('select page: %s' % url)
        self.client.download_posts(url, page_type, 
                incremental=self.client.can_incremental(page_type), refresh=not page_meta['login'])
        logger.info('page saved: %s' % url)

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
            self.focus_posts()

    def refresh(self):
        if self.state['loading'] or self.state['show_help'] or self.is_focus_login():
            return
        self.on_select_page(self.state['current_page_type'])

    def trigger_upvote(self):
        page_meta = self.hn_data.pages[self.state['current_page_type']]
        if self.state['loading'] \
                or self.state['show_help'] \
                or page_meta['login'] \
                or not self.is_focus_posts():
            return

        # must get focus data before all set_state, as after rerender, focus lost
        post = self.get_focus_post()

        self.load_posts('upvoted')
        posts_upvoted = self.get_posts('upvoted')
        if not posts_upvoted:
            return

        self.set_state({'loading': True, 'loading_content': 'updating upvote...'})
        upvoted = utils.get_post_identity(post) in map(lambda p: utils.get_post_identity(p), posts_upvoted)

        def bgf():
            self.client.upvote(post, upvoted)
            if upvoted:
                self.hn_data.remove_post('upvoted', post)
            self.download_posts('upvoted')
            self.load_posts('upvoted')
            # XXX: load_posts already change loading, don't set loading again, or ui will forzen
            # self.set_state({'loading': False})
            # self.refresh()

        threading.Thread(target=bgf).start()

    def trigger_favorite(self):
        page_meta = self.hn_data.pages[self.state['current_page_type']]
        if self.state['loading'] \
                or self.state['show_help'] \
                or page_meta['login'] \
                or not self.is_focus_posts():
            return

        # must get focus data before all set_state, as after rerender, focus lost
        post = self.get_focus_post()

        self.load_posts('favorite')
        posts_favorite = self.get_posts('favorite')
        if not posts_favorite:
            return

        self.set_state({'loading': True, 'loading_content': 'updating favorite...'})
        favorited = utils.get_post_identity(post) in map(lambda p: utils.get_post_identity(p), posts_favorite)

        def bgf():
            self.client.favorite(post, favorited)
            self.download_posts('favorite')
            if favorited:
                self.hn_data.remove_post('favorite', post)
            self.load_posts('favorite')
            # XXX: load_posts already change loading, don't set loading again, or ui will forzen
            # self.set_state({'loading': False})
            # self.refresh()

        threading.Thread(target=bgf).start()

    def get_focus_post(self):
        # post_idx = self.root_el.contents[self.posts_focus_postion()][0].contents[1][0].original_widget.focus_position - 1
        identity = self.root_el.contents[self.posts_focus_postion()][0].contents[1][0].original_widget.get_focus_widgets()[2].identity
        post = [v for v in self.get_posts(self.state['current_page_type']) if utils.get_post_identity(v) == identity][0]
        return post

    def is_focus_login(self):
        return self.root_el.focus_position == 1 and len(self.root_el.contents) > 1

    def focus_login(self):
        self.root_el.focus_position = 1

    def is_focus_posts(self):
        pos = self.posts_focus_postion()
        l = len(self.root_el.contents)
        return self.root_el.focus_position == pos and l > 1 and self.root_el.contents[pos][0].focus_position == 1

    def focus_posts(self):
        self.root_el.focus_position = self.posts_focus_postion()

    def posts_focus_postion(self):
        return len(self.root_el.contents) - 1

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
        current_sort = self.state['current_sort']
        search_keyword = self.state['search_keyword']
        current_page_type = self.state['current_page_type']
        posts = self.get_posts(current_page_type)

        if current_sort != 'default':
            sort_map = dict(
                    score='score',
                    comment='comment_cnt',
                    )
            posts = sorted(posts, key=lambda x: x[sort_map[current_sort]], 
                    reverse=self.state['current_sort_dir'] == 'desc')

        if search_keyword:
            ks = search_keyword.split(' ')
            fn = lambda t: any(map(lambda k: k and k in t, ks))
            posts_searched = [p for p in posts
                              if fn(p['title'].lower())
                              or fn(p['cat'].lower())
                              or fn(p['auther'].lower())]
        else:
            posts_searched = posts
        posts_filtered = [p for p in posts_searched
                          if p['cat'] == current_cat or current_cat == 'all']

        loading_el = urwid.ListBox([urwid.Text(('reversed', 'CHN'), align='center')])
        if self.state['loading']:
            s = 'Loading %s...' % self.state['loading_content']
            loading_el = urwid.ListBox([urwid.Text(('loading', s), align='center')])

        self.login_el = React.create_element(LoginForm, 'login', 
                is_login=is_login, on_login=self.on_login, 
                username=self.state['username'], password=self.state['password'],
                set_username=self.set_username, set_password=self.set_password,
                search_keyword=self.state['search_keyword'], on_search=self.on_search)
        page_btns_el = React.create_element(PageBtns, 'page_btns', 
                is_login=is_login, pages=self.hn_data.pages,
                on_select_page=self.on_select_page)
        side_bar_el = React.create_element(SideBar, 'side_bar', posts=posts_searched, 
                on_select_cat=self.on_select_cat, on_select_sort=self.on_select_sort)
        posts_el = React.create_element(Posts, 'posts',
                posts=posts_filtered, page_type=current_page_type,
                posts_upvoted=self.get_posts('upvoted'), posts_favorite=self.get_posts('favorite'))
        body_el = urwid.Columns([('weight', 2, side_bar_el), ('weight', 10, posts_el)])

        return [
            (loading_el, ('weight', .2)), 
            (self.login_el, ('weight', .5)), 
            (page_btns_el, ('weight', .5)), 
            # (side_bar_el, ('weight', .5)),
            # (posts_el, ('weight', 10))
            (body_el, ('weight', 10))
        ]


palette = [
        ('reversed', 'standout', ''),
        ('loading', 'yellow', 'dark green'),
        ('cat', 'dark green', ''),
        ('subtext', 'dark gray', ''),
        ('highlight', 'dark red', ''),

        ('headings', 'white,underline', 'black', 'bold,underline'),
        ('body_text', 'dark cyan', 'light gray'),
        ('buttons', 'yellow', 'dark green', 'standout'),
        ('section_text', 'body_text'),
]

if __name__ == '__main__':
    from train import *
    root_el = HnPile([])
    ReactConsole.render(React.create_element(App, 'app', root_el=root_el, return_instance=True), 
            root_el, palette=palette)

