from core.screen.base_screen import BaseScreen


class ScreenManager:
    def __init__(self):
        self.current = None

    def set(self, screen: BaseScreen):
        self.current = screen
        self.current.on_enter()

    def draw(self):
        if self.current:
            self.current.draw()