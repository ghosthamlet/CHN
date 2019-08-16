#coding=utf8

import urwid


class Component:
    def __init__(self):
        self.state = {}

    def set_state(self, m, 
                  disable_render=False):
        for k, v in m.items():
            self.state[k] = v

        if not disable_render:
            React.root_el.contents = self.render()

    def render(self):
        pass


class React:
    root_el = urwid.Pile([])

    def render(app):
        React.root_el.contents = app.render()
        urwid.MainLoop(React.root_el, palette=[('reversed', 'standout', '')]).run()
