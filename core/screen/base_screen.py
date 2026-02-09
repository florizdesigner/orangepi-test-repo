class BaseScreen:
    def __init__(self, ui, manager):
        self.ui = ui
        self.manager = manager

    def on_enter(self): pass
    def on_exit(self): pass
    def on_event(self, evt, data): pass
    def draw(self): pass
