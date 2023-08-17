import json

class ChatManager:
    """
    Класс для управления данными о чатах и их настройках.

    Аргументы:
        file_name (str): Имя файла JSON для хранения данных о чатах.

    Методы:
        load_chats(): Загрузить данные о чатах из файла JSON.
        save_chats(chats): Сохранить данные о чатах в файл JSON.
        add_chat(chat_id, chat_data): Добавить новый чат с указанным chat_id и начальными данными.
        remove_chat(chat_id): Удалить чат с указанным chat_id.
        get_chat_data(chat_id): Получить данные чата по указанному chat_id.
        update_chat_data(chat_id, key, value): Обновить данные чата по указанному chat_id и ключу.
    """

    def __init__(self, file_name):
        self.file_name = file_name

    def load_chats(self):
        """
        Загружает данные о чатах из файла JSON.

        Возвращает:
            dict: Словарь с данными о чатах.
        """
        try:
            with open(self.file_name, "r", encoding="utf-8") as file:
                chats = json.load(file)
        except FileNotFoundError:
            chats = {}
        return chats

    def save_chats(self, chats):
        """
        Сохраняет данные о чатах в файл JSON.

        Аргументы:
            chats (dict): Словарь с данными о чатах.
        """
        with open(self.file_name, "w", encoding="utf-8") as file:
            json.dump(chats, file, indent=4, ensure_ascii=False)

    def add_chat(self, chat_id, chat_name):
        """
        Добавляет чат с заданным chat_id и названием.

        Аргументы:
            chat_id (int): chat_id чата.
            chat_name (str): Название чата.
        """
        chats = self.load_chats()
        if chat_id not in chats:
            chats[chat_id] = {
                "title": chat_name,
                "welcome_message": f"Приветствую тебя в нашем чате {chat_name}!",
                "send_weather": True,
                "send_currency": True,
                "send_purchase_currency": True,
                "sending_messages": True,
                }
            self.save_chats(chats)

    def remove_chat(self, chat_id):
        """
        Удаляет чат с указанным chat_id.

        Аргументы:
            chat_id (str): Уникальный идентификатор чата.
        """
        chats = self.load_chats()
        if chat_id in chats:
            del chats[chat_id]
            self.save_chats(chats)

    def get_chat_data(self, chat_id):
        """
        Получает данные чата по указанному chat_id.

        Аргументы:
            chat_id (str): Уникальный идентификатор чата.

        Возвращает:
            dict: Данные чата.
        """
        chat_id = str(chat_id)
        chats = self.load_chats()
        return chats.get(chat_id, {})

    def update_chat_data(self, chat_id, key, value):
        """
        Обновляет данные чата по указанному chat_id и ключу.

        Аргументы:
            chat_id (str): Уникальный идентификатор чата.
            key (str): Ключ для обновления данных.
            value: Новое значение для обновления.

        Примечание:
            Если чат с указанным chat_id не существует, данные не будут обновлены.
        """
        chats = self.load_chats()
        if chat_id in chats:
            chats[chat_id][key] = value
            self.save_chats(chats)

    def get_all_chat_ids(self):
        """
        Получает список всех chat_id чатов.

        Возвращает:
            list: Список chat_id всех чатов.
        """
        chats = self.load_chats()
        return list(chats.keys())

    @staticmethod
    def get_all_chat_ids_static(file_name):
        """
        Получает список всех ID чатов.

        Аргументы:
            file_name (str): Имя файла JSON для хранения данных о чатах.

        Возвращает:
            list: Список ID чатов.
        """
        with open(file_name, "r") as file:
            try:
                data = json.load(file)
                chats = list(data.keys())
            except (json.JSONDecodeError, KeyError):
                chats = {}
        return chats