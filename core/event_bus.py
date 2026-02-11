class EventBus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event, callback):
        self._subscribers.setdefault(event, []).append(callback)

    def emit(self, event, *args, **kwargs):
        # Делаем копию списка, чтобы безопасно изменять подписки во время обхода
        for cb in list(self._subscribers.get(event, [])):
            cb(*args, **kwargs)

    def unsubscribe(self, event, callback):
        """Отписка конкретного обработчика от события."""
        callbacks = self._subscribers.get(event)
        if not callbacks:
            return
        try:
            callbacks.remove(callback)
        except ValueError:
            # Такой подписки уже нет — просто игнорируем
            return
        if not callbacks:
            # Чистим пустой список подписчиков
            del self._subscribers[event]
