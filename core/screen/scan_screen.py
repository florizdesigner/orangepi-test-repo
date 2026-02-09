from core.screen.base_screen import BaseScreen
from core.screen.main_screen import MainScreen


class ScanScreen(BaseScreen):
    def __init__(self, ui, manager):
        super().__init__(ui)
        self.manager = manager

        ui.bus.subscribe("btn.MID", self.back)

    def on_enter(self):
        self.ui.tasks.toggle("rfid")

    def back(self):
        self.ui.tasks.toggle("rfid")
        self.manager.set(MainScreen(self.ui, self.manager))

    def draw(self):
        d = self.ui.draw
        d.rectangle((0, 0, self.ui.W, self.ui.H), fill=(0, 0, 20))

        d.text((20, 40), "RFID SCAN MODE", font=self.ui.font_big, fill=(0,255,255))
        d.text((20, 100), "Scanning...", font=self.ui.font_mid, fill=(255,255,255))
        d.text((20, 180), "RST = Back", font=self.ui.font_small, fill=(150,150,150))

        self.ui.disp.display(self.ui.image)
