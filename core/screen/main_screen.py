from core.screen.base_screen import BaseScreen
from core.screen.scan_screen import ScanScreen


class MainScreen(BaseScreen):
    def __init__(self, ui, manager):
        super().__init__(ui)
        self.manager = manager
        self.items = [
            ("Scan", ScanScreen),
            # ("Write", WriteScreen),
            # ("Info", InfoScreen),
        ]
        self.selected = 0

        ui.bus.subscribe("btn.DOWN", self.down)
        ui.bus.subscribe("btn.UP", self.up)
        ui.bus.subscribe("btn.MID", self.select)

    def down(self):
        self.selected = (self.selected + 1) % len(self.items)
        self.draw()

    def up(self):
        self.selected = (self.selected - 1) % len(self.items)
        self.draw()

    def select(self):
        screen_cls = self.items[self.selected][1]
        self.manager.set(screen_cls(self.ui, self.manager))

    def draw(self):
        d = self.ui.draw
        d.rectangle((0, 0, self.ui.W, self.ui.H), fill=(0, 0, 0))

        y = 80
        for i, (name, _) in enumerate(self.items):
            prefix = ">" if i == self.selected else " "
            d.text((30, y), f"{prefix} {name}", font=self.ui.font_big, fill=(255,255,255))
            y += 50

        self.ui.disp.display(self.ui.image)
