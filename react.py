#coding=utf8

import urwid


_APP = None
_ROOT_EL = urwid.Pile([])


class Component:
    instances = {}

    @classmethod
    def factory(cls, instance_name, **props):
        obj = Component.instances.get(instance_name)

        if obj is not None:
            obj.props = props
        else:
            obj = cls(**props)
            Component.instances[instance_name] = obj

        return obj

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

    def render(self):
        pass


class React:
    def render(app):
        global _APP
        _APP = app
        _ROOT_EL.contents = app.render()
        urwid.MainLoop(_ROOT_EL, palette=[('reversed', 'standout', '')]).run()
