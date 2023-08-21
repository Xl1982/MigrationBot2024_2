import json

class TextMessagesStorage:
    """
    Класс для работы с хранением и управлением текстовыми сообщениями в формате JSON.

    Атрибуты:
        file_path (str): Путь к JSON-файлу, в котором хранятся данные сообщений.

    Методы:
        __init__(file_path): Конструктор класса. Инициализирует объект класса с указанным путем к JSON-файлу.
        migrate_old_format_for_chat(chat_id): Метод для приведения старого формата данных к новому для указанного чата.
        add_message(chat_id, day_of_week, time_sent, text, photos=None, videos=None): Добавляет текстовое сообщение с указанным временем отправки к определенному дню недели и чату.
        delete_message(chat_id, day_of_week, time_sent): Удаляет указанное текстовое сообщение с определенного дня недели по времени отправки и чату.
        get_messages_for_day(chat_id, day_of_week): Возвращает список словарей с текстовыми сообщениями для указанного дня недели и чата.

    Пример использования:
        storage = TextMessagesStorage('text_messages.json')
        storage.migrate_old_format_for_chat('global')
        storage.add_message('global', 'Monday', '09:00', 'Привет!', photos=['photo1.jpg'], videos=['video1.mp4'])
        storage.add_message('global', 'Monday', '14:30', 'Как дела?')
        messages = storage.get_messages_for_day('global', 'Monday')
        for message in messages:
            time_sent = message['time_sent']
            text = message['text']
            photos = message['photos']
            videos = message['videos']
            print(f"Время: {time_sent}, Текст: {text}, Фото: {photos}, Видео: {videos}")
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
            dict: Словарь с данными текстовых сообщений, где ключ - chat_id, значение - вложенный словарь с информацией о сообщениях.
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

    def _migrate_old_format(self, chat_id):
        new_data = {chat_id: self.data}
        self.data = new_data
        self._save_data()

    def migrate_old_format_for_chat(self, chat_id):
        """
        Метод для приведения старого формата данных к новому для указанного чата.

        Параметры:
            chat_id (str): Идентификатор чата.
        """
        self._migrate_old_format(chat_id)

    def add_message(self, chat_id, day_of_week, time_sent, text, photos=None, videos=None):
        """
        Добавляет текстовое сообщение с указанным временем отправки к определенному дню недели и чату.

        Параметры:
            chat_id (str): Идентификатор чата.
            day_of_week (str): Название дня недели.
            time_sent (str): Время отправки сообщения в формате 'ЧЧ:ММ'.
            text (str): Текстовое сообщение.
            photos (list): Список файловых идентификаторов фотографий (по умолчанию None).
            videos (list): Список файловых идентификаторов видео (по умолчанию None).
        """
        chat_id = str(chat_id)
        if chat_id not in self.data:
            self.data[chat_id] = {}
        if day_of_week not in self.data[chat_id]:
            self.data[chat_id][day_of_week] = []
        message = {'time_sent': time_sent, 'text': text, 'photos': photos or [], 'videos': videos or []}
        self.data[chat_id][day_of_week].append(message)
        self._save_data()

    def delete_message(self, chat_id, day_of_week, time_sent):
        """
        Удаляет указанное текстовое сообщение с определенного дня недели по времени отправки и чату.

        Параметры:
            chat_id (str): Идентификатор чата.
            day_of_week (str): Название дня недели.
            time_sent (str): Время отправки сообщения в формате 'ЧЧ:ММ'.
        """
        chat_id = str(chat_id)
        if chat_id in self.data and day_of_week in self.data[chat_id]:
            self.data[chat_id][day_of_week] = [message for message in self.data[chat_id][day_of_week] if message['time_sent'] != time_sent]
            self._save_data()

    def get_messages_for_day(self, chat_id, day_of_week):
        """
        Возвращает список словарей с текстовыми сообщениями для указанного дня недели и чата.

        Параметры:
            chat_id (str): Идентификатор чата.
            day_of_week (str): Название дня недели.

        Возвращает:
            list: Список словарей, где каждый словарь представляет собой сообщение с ключами 'time_sent', 'text', 'photos' и 'videos'.
        """
        chat_id = str(chat_id)
        return self.data.get(chat_id, {}).get(day_of_week, [])
