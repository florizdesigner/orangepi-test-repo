import logging
from core.screen.base_screen import BaseScreen

logger = logging.getLogger(__name__)

class ScanScreen(BaseScreen):

    def __init__(self, ui, manager):
        super().__init__(ui, manager)
        self.uid = "---"
        self.current_event_id = None
        self.event_name = "---"
        self.user_name = "---"

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
            logger.info(f"Вошли в on_event: {data}")
            self.uid = data
            # Получаем данные о пользователе и формируем строку
            self._get_user_info(data)
            # Отправляем запрос /finish с userId и eventId
            self._finish_event(data)

    def back(self):
        self.manager.set("main")

    def _get_user_info(self, user_id: str):
        result = self.ui.api_client.get_user(user_id)
        username = _format_user_info(result)
        self.user_name = username

    def _format_user_info(result):
        first_name = result['first_name'] | None
        last_name = result['last_name'] | None
        username = result['username'] | None

        # Собираем имя и фамилию
        name_parts = [part for part in [first_name, last_name] if part]
        full_name = " ".join(name_parts) if name_parts else None

        # Формируем итоговую строку
        if full_name and username:
            return f"{full_name} ({username})"
        elif full_name:
            return full_name
        elif username:
            return username
        else:
            return ""  # или можно вернуть "Unknown User"

    def _load_active_event(self):
        """Загружает последний активный event через API"""
        if not self.ui.api_client:
            logger.warning("API client not available")
            self.event_name = "API недоступен"
            return
        
        try:
            # Получаем список активных событий
            events = self.ui.api_client.get_active_events()
            
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
            event_id = self.current_event_id
            success = self.ui.api_client.finish_event(event_id, user_id)
            
            if success:
                logger.info(f"Event finished successfully: event_id={event_id}, user_id={user_id}")
            else:
                logger.error(f"Failed to finish event: event_id={event_id}, user_id={user_id}")
        except Exception as e:
            logger.error(f"Error finishing event: {e}")

    # def draw(self):
    #     d = self.ui.draw
    #     d.rectangle((0, 0, self.ui.W, self.ui.H), fill=(0, 0, 20))
    #
    #     d.text((16, 10), "RFID SCAN", font=self.ui.font_big, fill=(0,255,255))
    #
    #     # Показываем название активного события
    #     event_text = f"Event: {self.event_name[:15]}" if len(self.event_name) > 15 else f"Event: {self.event_name}"
    #     d.text((16, 45), event_text, font=self.ui.font_small, fill=(150,150,150))
    #
    #     d.text((16, 70), "LAST UID:", font=self.ui.font_mid, fill=(180,180,180))
    #
    #     d.rectangle((10, 95, self.ui.W-10, 135), outline=(0,255,255))
    #
    #     d.text((20, 105), self.uid, font=self.ui.font_mid, fill=(255,255,255))
    #
    #     d.text((16, self.ui.H - 25), "RST = Back", font=self.ui.font_small, fill=(150,150,150))
    #
    #     self.ui.disp.display(self.ui.image)

    def draw(self):
        d = self.ui.draw
        d.rectangle((0, 0, self.ui.W, self.ui.H), fill=(0, 0, 20))

        d.text((16, 10), "RFID SCAN", font=self.ui.font_big, fill=(0, 255, 255))

        # Показываем название активного события (обрезаем до 18 символов)
        event_text = self.event_name[:18] + "..." if len(self.event_name) > 18 else self.event_name
        d.text((16, 40), f"Event: {event_text}", font=self.ui.font_small, fill=(150, 150, 150))

        d.text((16, 65), "LAST SCAN:", font=self.ui.font_mid, fill=(180, 180, 180))

        # Компактная область для UID и имени
        d.rectangle((10, 90, 230, 160), outline=(0, 255, 255))

        # UID - обрезаем если очень длинный
        uid_display = self.uid[:22] if len(self.uid) > 22 else self.uid
        d.text((16, 98), uid_display, font=self.ui.font_small, fill=(255, 255, 255))

        # Имя пользователя (если есть) - обрезаем до 22 символов
        if self.user_name:
            name_display = self.user_name[:22] + "..." if len(self.user_name) > 22 else self.user_name
            d.text((16, 118), name_display, font=self.ui.font_small, fill=(100, 200, 255))
        else:
            # Если имени нет, показываем placeholder
            d.text((16, 118), "Unknown user", font=self.ui.font_small, fill=(80, 80, 80))

        # Если есть место, можно добавить статус
        d.text((16, 145), "Status: OK", font=self.ui.font_small, fill=(0, 255, 100))

        d.text((16, 215), "RST = Back", font=self.ui.font_small, fill=(150, 150, 150))

        self.ui.disp.display(self.ui.image)