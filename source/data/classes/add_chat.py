import json

class ChatManager:
    """
    Класс для управления чатами и взаимодействия с ними.

    Аргументы:
        file_name (str): Имя файла JSON для хранения данных о чатах.

    Методы:
        load_chats(): Загрузить данные о чатах из файла JSON.
        save_chats(chats): Сохранить данные о чатах в файл JSON.
        add_chat(chat_id, chat_name): Добавить чат с заданным ID и названием.
        remove_chat(chat_id): Удалить чат с заданным ID.
        get_all_chat_ids(): Получить список всех ID чатов.
        get_all_chats(): Получить словарь со всеми чатами и их названиями.
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
            with open(self.file_name, "r") as file:
                try:
                    data = json.load(file)
                    chats = data.get("chats", {})
                except (json.JSONDecodeError, KeyError):
                    chats = {}
        except FileNotFoundError:
            chats = {}
        return chats

    def save_chats(self, chats):
        """
        Сохраняет данные о чатах в файл JSON.

        Аргументы:
            chats (dict): Словарь с данными о чатах.
        """
        data = {"chats": chats}
        with open(self.file_name, "w") as file:
            json.dump(data, file)

    def add_chat(self, chat_id, chat_name):
        """
        Добавляет чат с заданным ID и названием.

        Аргументы:
            chat_id (int): ID чата.
            chat_name (str): Название чата.
        """
        chats = self.load_chats()
        if chat_id not in chats:
            chats[chat_id] = chat_name
            self.save_chats(chats)

    def remove_chat(self, chat_id):
        """
        Удаляет чат с заданным ID.

        Аргументы:
            chat_id (int): ID чата.
        """
        chats = self.load_chats()
        if chat_id in chats:
            del chats[chat_id]
            self.save_chats(chats)

    def get_all_chat_ids(self):
        """
        Получает список всех ID чатов.

        Возвращает:
            list: Список ID чатов.
        """
        chats = self.load_chats()
        return list(chats.keys())

    def get_all_chats(self):
        """
        Получает словарь со всеми чатами и их названиями.

        Возвращает:
            dict: Словарь с парами ID чата и их названиями.
        """
        return self.load_chats()