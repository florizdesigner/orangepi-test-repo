class ScreenManager:
    def __init__(self, ui):
        self.ui = ui
        self.screens = {}
        # Кеш готовых инстансов экранов, чтобы не дублировать подписки на события
        self._instances = {}
        self.current = None

    def register(self, name, screen_cls):
        self.screens[name] = screen_cls

    def set(self, name):
        if self.current:
            self.current.on_exit()

        # Лениво создаём экран один раз и переиспользуем его,
        # чтобы __init__ (и подписки на шину событий) не вызывались многократно.
        if name not in self._instances:
            self._instances[name] = self.screens[name](self.ui, self)

        self.current = self._instances[name]
        self.current.on_enter()

    def draw(self):
        if self.current:
            self.current.draw()

    def event(self, evt, data):
        if self.current:
            self.current.on_event(evt, data)