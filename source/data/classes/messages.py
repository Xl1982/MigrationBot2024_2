import json


class TextMessagesStorage:
    """
    Класс для работы с хранением и управлением текстовыми сообщениями в формате JSON.

    Атрибуты:
        file_path (str): Путь к JSON-файлу, в котором хранятся данные сообщений.

    Методы:
        __init__(file_path): Конструктор класса. Инициализирует объект класса с указанным путем к JSON-файлу.
        add_message(day_of_week, time_sent, message): Добавляет текстовое сообщение с указанным временем отправки к определенному дню недели.
        delete_message(day_of_week, time_sent): Удаляет указанное текстовое сообщение с определенного дня недели по времени отправки.
        get_messages_for_day(day_of_week): Возвращает словарь с текстовыми сообщениями для указанного дня недели.

    Пример использования:
        storage = TextMessagesStorage('text_messages.json')
        storage.add_message('Monday', '09:00', 'Привет!')
        storage.add_message('Monday', '14:30', 'Как дела?')
        messages = storage.get_messages_for_day('Monday')
        for time_sent, message in messages.items():
            print(f"Время: {time_sent}, Текст: {message}")
    """

    def __init__(self, file_path):
        """
        Инициализирует объект класса TextMessagesStorage с указанным путем к JSON-файлу.

        Параметры:
            file_path (str): Путь к JSON-файлу, в котором хранятся данные сообщений.
        """
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self):
        """
        Загружает данные из JSON-файла.

        Возвращает:
            dict: Словарь с данными текстовых сообщений, где ключ - день недели, значение - словарь со временем отправки и текстовым сообщением.
        """
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_data(self):
        """
        Сохраняет данные в JSON-файл.
        """
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def add_message(self, day_of_week, time_sent, text, chat_id, photos=None):
        """
        Добавляет текстовое сообщение с указанным временем отправки к определенному дню недели.

        Параметры:
            day_of_week (str): Название дня недели.
            time_sent (str): Время отправки сообщения в формате 'ЧЧ:ММ'.
            text (str): Текстовое сообщение.
            photos (list): Список файловых идентификаторов фотографий (по умолчанию None).
        """
        if day_of_week not in self.data:
            self.data[day_of_week] = []
        message = {'time_sent': time_sent, 'text': text, 'chat_id': chat_id, 'photos': photos or []}
        self.data[day_of_week].append(message)
        self._save_data()

    def delete_message(self, day_of_week, time_sent):
        """
        Удаляет указанное текстовое сообщение с определенного дня недели по времени отправки.

        Параметры:
            day_of_week (str): Название дня недели.
            time_sent (str): Время отправки сообщения в формате 'ЧЧ:ММ'.
        """
        if day_of_week in self.data and time_sent in self.data[day_of_week]:
            del self.data[day_of_week][time_sent]
            self._save_data()

    def get_messages_for_day(self, day_of_week):
        """
        Возвращает список словарей с текстовыми сообщениями для указанного дня недели.

        Параметры:
            day_of_week (str): Название дня недели.

        Возвращает:
            list: Список словарей, где каждый словарь представляет собой сообщение с ключами 'time_sent', 'text' и 'photos'.
        """
        return self.data.get(day_of_week, [])
