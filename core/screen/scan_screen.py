import logging
from core.screen.base_screen import BaseScreen

logger = logging.getLogger(__name__)

class ScanScreen(BaseScreen):

    def __init__(self, ui, manager):
        super().__init__(ui, manager)
        self.uid = "---"
        self.current_event_id = None
        self.event_name = "---"

        # Подписку на кнопки переносим в on_enter/on_exit,
        # чтобы можно было безопасно отписываться

    def on_enter(self):
        # Сбрасываем UID при каждом входе на экран
        self.uid = "---"
        self.current_event_id = None
        self.event_name = "---"
        
        # Запрашиваем активный event через API
        self._load_active_event()
        
        self.ui.bus.subscribe("btn.RST", self.back)
        self.ui.tasks.toggle("rfid")

    def on_exit(self):
        self.ui.bus.unsubscribe("btn.RST", self.back)
        self.ui.tasks.toggle("rfid")

    def on_event(self, evt, data):
        if evt == "rfid.uid":
            self.uid = data
            # Отправляем запрос /finish с userId и eventId
            self._finish_event(data)

    def back(self):
        self.manager.set("main")

    def _load_active_event(self):
        """Загружает последний активный event через API"""
        if not self.ui.api_client:
            logger.warning("API client not available")
            self.event_name = "API недоступен"
            return
        
        try:
            # Получаем список активных событий
            events = self.ui.api_client.get_events(status='IN_ACTIVE')
            
            if events and len(events) > 0:
                # Берем последний активный event (первый в списке или последний по дате)
                # Предполагаем, что API возвращает события отсортированными
                active_event = events[0]
                self.current_event_id = active_event.get('id')
                self.event_name = active_event.get('title', 'Unknown')
                logger.info(f"Active event loaded: {self.event_name} (ID: {self.current_event_id})")
            else:
                self.current_event_id = None
                self.event_name = "Нет активных событий"
                logger.warning("No active events found")
        except Exception as e:
            logger.error(f"Failed to load active event: {e}")
            self.event_name = "Ошибка загрузки"
            self.current_event_id = None

    def _finish_event(self, user_id: str):
        """Отправляет запрос /finish с userId и eventId"""
        if not self.current_event_id:
            logger.warning(f"Cannot finish event: no active event. User ID: {user_id}")
            return
        
        if not self.ui.api_client:
            logger.warning("API client not available")
            return
        
        try:
            # Преобразуем event_id в int, если нужно
            event_id = int(self.current_event_id)
            success = self.ui.api_client.finish_event(event_id, user_id)
            
            if success:
                logger.info(f"Event finished successfully: event_id={event_id}, user_id={user_id}")
            else:
                logger.error(f"Failed to finish event: event_id={event_id}, user_id={user_id}")
        except Exception as e:
            logger.error(f"Error finishing event: {e}")

    def draw(self):
        d = self.ui.draw
        d.rectangle((0, 0, self.ui.W, self.ui.H), fill=(0, 0, 20))

        d.text((16, 10), "RFID SCAN", font=self.ui.font_big, fill=(0,255,255))
        
        # Показываем название активного события
        event_text = f"Event: {self.event_name[:15]}" if len(self.event_name) > 15 else f"Event: {self.event_name}"
        d.text((16, 45), event_text, font=self.ui.font_small, fill=(150,150,150))
        
        d.text((16, 70), "LAST UID:", font=self.ui.font_mid, fill=(180,180,180))

        d.rectangle((10, 95, self.ui.W-10, 135), outline=(0,255,255))

        d.text((20, 105), self.uid, font=self.ui.font_mid, fill=(255,255,255))

        d.text((16, self.ui.H - 25), "RST = Back", font=self.ui.font_small, fill=(150,150,150))

        self.ui.disp.display(self.ui.image)
