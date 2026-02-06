import threading

class ToggleTask:
    def __init__(self, target):
        self.target = target
        self.event = threading.Event()
        self.thread = None
        self.lock = threading.Lock()

    def start(self):
        with self.lock:
            if self.thread and self.thread.is_alive():
                return
            self.event.set()
            self.thread = threading.Thread(
                target=self.target,
                args=(self.event,),
                daemon=True
            )
            self.thread.start()

    def stop(self):
        with self.lock:
            self.event.clear()

    def toggle(self):
        if self.thread and self.thread.is_alive():
            self.stop()
        else:
            self.start()

class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.active = None
        self.lock = threading.Lock()

    def register(self, name, func):
        self.tasks[name] = ToggleTask(func)

    def toggle(self, name):
        with self.lock:
            if self.active == name:
                self.tasks[name].stop()
                self.active = None
                return

            if self.active:
                self.tasks[self.active].stop()

            self.tasks[name].start()
            self.active = name