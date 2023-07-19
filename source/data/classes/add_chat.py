import json

class ChatManager:
    def __init__(self, file_name):
        self.file_name = file_name

    def load_chats(self):
        try:
            with open(self.file_name, "r") as file:
                try:
                    data = json.load(file)
                    chats = data["chats"]
                except (json.JSONDecodeError, KeyError):
                    chats = []
        except FileNotFoundError:
            chats = []
        return chats

    def save_chats(self, chats):
        data = {"chats": chats}
        with open(self.file_name, "w") as file:
            json.dump(data, file)

    def add_chat(self, chat_id):
        chats = self.load_chats()
        if chat_id not in chats:
            chats.append(chat_id)
            self.save_chats(chats)

    def remove_chat(self, chat_id):
        chats = self.load_chats()
        if chat_id in chats:
            chats.remove(chat_id)
            self.save_chats(chats)

    def get_all_chats(self):
        return self.load_chats()