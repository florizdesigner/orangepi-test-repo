import time

class BaseScreen:
    def __init__(self, ui, manager):
        self.ui = ui
        self.manager = manager
        # Состояние pop-up
        self._popup_text = None
        self._popup_type = None  # 'success', 'error', 'warn'
        self._popup_start_time = None
        self._popup_duration = 0

    def on_enter(self): pass
    def on_exit(self): pass
    def on_event(self, evt, data): pass
    
    def _draw_content(self):
        """Переопределяется в дочерних классах для рисования основного содержимого"""
        pass
    
    def show_popup(self, text, popup_type='warn', duration=3):
        """
        Показывает pop-up поверх экрана
        
        Args:
            text: Текст для отображения
            popup_type: Тип pop-up ('success', 'error', 'warn')
            duration: Количество секунд до автоматического закрытия
        
        Example:
            # Показать предупреждение на 3 секунды
            self.show_popup("Ошибка подключения", popup_type='error', duration=3)
            
            # Показать успешное сообщение на 2 секунды
            self.show_popup("Операция выполнена успешно", popup_type='success', duration=2)
        """
        self._popup_text = text
        self._popup_type = popup_type
        self._popup_duration = duration
        self._popup_start_time = time.time()
    
    def _draw_popup(self):
        """Рисует pop-up поверх основного содержимого"""
        if self._popup_text is None:
            return
        
        # Проверяем, не истекло ли время показа
        if self._popup_start_time and time.time() - self._popup_start_time >= self._popup_duration:
            self._popup_text = None
            self._popup_type = None
            self._popup_start_time = None
            return
        
        d = self.ui.draw
        
        # Определяем цвет в зависимости от типа
        if self._popup_type == 'success':
            bg_color = (0, 150, 0)
            border_color = (0, 255, 100)
            text_color = (255, 255, 255)
        elif self._popup_type == 'error':
            bg_color = (150, 0, 0)
            border_color = (255, 50, 50)
            text_color = (255, 255, 255)
        else:  # warn
            bg_color = (150, 100, 0)
            border_color = (255, 200, 0)
            text_color = (255, 255, 255)
        
        # Размеры pop-up
        padding = 10
        popup_width = self.ui.W - 20
        popup_height = 60
        popup_x = 10
        popup_y = (self.ui.H - popup_height) // 2
        
        # Рисуем фон pop-up
        d.rectangle(
            (popup_x, popup_y, popup_x + popup_width, popup_y + popup_height),
            fill=bg_color,
            outline=border_color
        )
        
        # Разбиваем текст на строки, если он слишком длинный
        max_chars_per_line = 25
        words = self._popup_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars_per_line:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Ограничиваем количество строк (максимум 2)
        lines = lines[:2]
        
        # Рисуем текст
        text_y = popup_y + 15
        for i, line in enumerate(lines):
            d.text(
                (popup_x + padding, text_y + i * 20),
                line,
                font=self.ui.font_small,
                fill=text_color
            )
    
    def draw(self):
        """Основной метод рисования - сначала содержимое, затем pop-up"""
        self._draw_content()
        self._draw_popup()
        self.ui.disp.display(self.ui.image)
