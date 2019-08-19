#coding=utf8

import random

import urwid


_APP = None
_ROOT_EL = None


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
                _ROOT_EL.contents = _APP.render()

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
            # el = obj.render()
            obj.component_did_mount()
            el = obj.render()
            React.instances[instance_name] = obj

        return (obj, el) if return_instance else el


class ReactConsole:
    def render(app, root_el):
        global _APP, _ROOT_EL
        _ROOT_EL = root_el
        _APP, _ROOT_EL.contents = app
        urwid.MainLoop(_ROOT_EL, palette=[('reversed', 'standout', '')]).run()

