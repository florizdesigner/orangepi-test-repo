class EventBus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event, callback):
        self._subscribers.setdefault(event, []).append(callback)

    def emit(self, event, *args, **kwargs):
        for cb in self._subscribers.get(event, []):
            cb(*args, **kwargs)
