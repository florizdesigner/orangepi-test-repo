class ScreenManager:
    def __init__(self, ui):
        self.ui = ui
        self.screens = {}
        self.current = None

    def register(self, name, screen_cls):
        self.screens[name] = screen_cls

    def set(self, name):
        if self.current:
            self.current.on_exit()

        self.current = self.screens[name](self.ui, self)
        self.current.on_enter()

    def draw(self):
        if self.current:
            self.current.draw()

    def event(self, evt, data):
        if self.current:
            self.current.on_event(evt, data)
