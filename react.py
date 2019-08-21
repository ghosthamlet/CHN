#coding=utf8

import os
import random

import urwid


_APP = None
_ROOT_EL = None
_UPDATE_PIPE = None


def _update_screen():
    os.write(_UPDATE_PIPE, b'1')


class Component:
    def __init__(self, **props):
        self.props = props
        self.state = {}

    def set_state(self, m, 
                  disable_render=False):
        for k, v in m.items():
            self.state[k] = v

        if not disable_render:
            # TODO: just render self
            # self.contents = self.render()
            if _APP is not None:
                self.mount(_APP.render())
                # for async update
                _update_screen()

    def mount(self, el):
        _ROOT_EL.contents = el

    def component_did_mount(self):
        pass

    def render(self):
        pass


class React:
    instances = {}
    n_element = 0

    def create_element(type, instance_name, return_instance=False, **props):
        random.seed(React.n_element)
        React.n_element += 1

        obj = React.instances.get(instance_name)

        if obj is not None:
            obj.props = props
            el = obj.render()
        else:
            obj = type(**props)
            if _APP is not None:
                el = obj.render()
                obj.component_did_mount()
            else:
                # TODO: move component_did_mount to after render
                #       now component_did_mount have to call before render, 
                #       or state in component_did_mount can't take effects
                obj.component_did_mount()
                el = obj.render()
            React.instances[instance_name] = obj

        return (obj, el) if return_instance else el


def _unhandled(key):
    if key == 'ctrl c' or key in ('q', 'Q'):
        raise urwid.ExitMainLoop()


class ReactConsole:
    def render(app, root_el, palette=None):
        global _APP, _ROOT_EL, _UPDATE_PIPE

        # reset for dev in repl
        React.instances = {}

        _ROOT_EL = root_el
        _APP, el = app
        _APP.mount(el)

        loop = urwid.MainLoop(_ROOT_EL, palette=palette, unhandled_input=_unhandled)
        # for async update
        # see main in https://github.com/zulip/zulip-terminal/blob/master/zulipterminal/core.py
        # http://urwid.org/reference/main_loop.html#selecteventloop
        # https://github.com/urwid/urwid/commit/83b64fee60fd77bc80f3dda307c74b53b35f6581
        _UPDATE_PIPE = loop.watch_pipe(lambda *x, **xs: loop.draw_screen())

        loop.run()

