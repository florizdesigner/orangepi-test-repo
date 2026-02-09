class BaseScreen:
    def __init__(self, ui):
        self.ui = ui

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def draw(self):
        pass