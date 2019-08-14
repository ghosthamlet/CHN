#coding=utf8

import re

import urwid

from chn import HnData, HnCrawler, HnAnalyze


def create_menu(self, choices):
    body = []
    choices = ['All', *choices]
    for c in choices:
        button = urwid.Button(c)
        urwid.connect_signal(button, 'click', lambda el, choice: menu_item_chosen(self, choice), c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))

    focus_el = urwid.SimpleFocusListWalker(body)
    # have to wrap Columns/GridFlow in ListBox, or Pile can't work
    return urwid.ListBox([urwid.Columns(focus_el)])


def menu_item_chosen(self, choice):
    key = re.sub('\(.+\)', '', choice)
    posts = {url:p for url, p in self.get_posts(self.current_page_type).items()
             if p['cat'] == key or key == 'All'}
    self.page_el.contents[1] = (self.create_list(posts), ('weight', 8))


def create_list(choices):
    body = [urwid.Text('test'), urwid.Divider()]
    for c in choices:
        button = urwid.Button(c)
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


class HnConsole:
    def __init__(self):
        self.hn_data = HnData()
        self.crawle  = HnCrawler()
        self.analyze = HnAnalyze()

        self.current_page_type = 'hot'
        self.header_el = None

    def init(self, crawler_new=False):
        if crawler_new:
            self.crawle.save('/', 'hot')
        self.load_posts('hot')

    def render(self):
        header_el = self.create_header()
        ls_el = self.create_list(self.get_posts('hot'))

        # page = urwid.Frame(ls_el, header_el, focus_part='header')
        self.page_el = urwid.Pile([('weight', 1, header_el), ('weight', 8, ls_el)])
        urwid.MainLoop(self.page_el, palette=[('reversed', 'standout', '')]).run()

    def create_header(self):
        posts = {}
        for _, p in self.get_posts('hot').items():
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
        header_el = urwid.Padding(create_menu(self, choices), left=1, right=1)
        return header_el

    def load_posts(self, page_type):
        self.hn_data.load_posts(page_type)
        posts = self.get_posts(page_type)
        self.analyze.assoc_cat(posts)

    def get_posts(self, page_type):
        return self.hn_data.all_posts[page_type]

    def create_list(self, posts):
        choices = []
        posts_sorted = sorted(posts.items(), key=lambda x: x[1]['rank'])

        for url, p in posts_sorted:
            choices.append('%s. [%s] %s' % (p['rank'], p['cat'], p['title']))
        ls_el = urwid.Padding(create_list(choices), left=1, right=1)
        return ls_el


