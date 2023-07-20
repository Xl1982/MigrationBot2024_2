import json

class AdminsManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self):
        try:
            with open(self.file_path, 'r') as file:
                file_contents = file.read()
                if not file_contents:
                    # Если файл пуст, возвращаем пустой словарь
                    return {}
                return json.loads(file_contents)
        except FileNotFoundError:
            return {}
        
    def _save_data(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file)

    def add_admin(self, user_id, name):
        self.data[str(user_id)] = name
        self._save_data()

    def remove_admin(self, user_id):
        user_id_str = str(user_id)
        if user_id_str in self.data:
            del self.data[user_id_str]
            self._save_data()

    def get_all_admins(self):
        return self.data

    def get_admin_by_id(self, user_id):
        return self.data.get(str(user_id))
    
    def get_all_admin_user_ids(self):
        return [int(user_id) for user_id in self.data.keys()]