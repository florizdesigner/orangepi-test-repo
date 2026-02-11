from core.screen.base_screen import BaseScreen

class MainScreen(BaseScreen):

    def __init__(self, ui, manager):
        super().__init__(ui, manager)
        self.items = [
            ("Scan", "scan"),
            ("Write", "write"),
        ]
        self.selected = 0
        # Подписку на кнопки переносим в on_enter/on_exit,
        # чтобы можно было безопасно отписываться

    def on_enter(self):
        self.ui.bus.subscribe("btn.DOWN", self.next)
        self.ui.bus.subscribe("btn.MID", self.select)

    def on_exit(self):
        self.ui.bus.unsubscribe("btn.DOWN", self.next)
        self.ui.bus.unsubscribe("btn.MID", self.select)

    def next(self):
        self.selected = (self.selected + 1) % len(self.items)

    def select(self):
        screen_name = self.items[self.selected][1]
        self.manager.set(screen_name)

    def draw(self):
        d = self.ui.draw
        d.rectangle((0, 0, self.ui.W, self.ui.H), fill=(0, 0, 0))

        y = 80
        for i, (name, _) in enumerate(self.items):
            prefix = ">" if i == self.selected else " "
            d.text((30, y), f"{prefix} {name}", font=self.ui.font_big, fill=(255,255,255))
            y += 50

        self.ui.disp.display(self.ui.image)
