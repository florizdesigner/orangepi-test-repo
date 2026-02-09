from core.screen.base_screen import BaseScreen

class ScanScreen(BaseScreen):

    def __init__(self, ui, manager):
        super().__init__(ui, manager)
        self.uid = "---"

        ui.bus.subscribe("btn.RST", self.back)

    def on_enter(self):
        self.ui.tasks.toggle("rfid")

    def on_exit(self):
        self.ui.tasks.toggle("rfid")

    def on_event(self, evt, data):
        if evt == "rfid.uid":
            self.uid = data

    def back(self):
        self.manager.set("main")

    def draw(self):
        d = self.ui.draw
        d.rectangle((0, 0, self.ui.W, self.ui.H), fill=(0, 0, 20))

        d.text((20, 30), "RFID SCAN", font=self.ui.font_big, fill=(0,255,255))
        d.text((20, 90), "LAST UID:", font=self.ui.font_mid, fill=(180,180,180))

        d.rectangle((10, 120, self.ui.W-10, 170), outline=(0,255,255))

        d.text((20, 130), self.uid, font=self.ui.font_mid, fill=(255,255,255))

        d.text((20, 190), "RST = Back", font=self.ui.font_small, fill=(150,150,150))

        self.ui.disp.display(self.ui.image)
