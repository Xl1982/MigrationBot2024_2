import psycopg2

from .based_class import BaseDB


class User(BaseDB):
    def add_user(self, user_id, user_firstname, user_lastname=None, user_last_message=None, is_admin_banned=False):
        # создаем курсор для выполнения запросов
        cur = self.conn.cursor()
        # формируем запрос на вставку данных в таблицу
        query = f"""
            INSERT INTO users (user_id, user_firstname, user_lastname, user_last_message, is_admin_banned)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING;
        """
        # выполняем запрос с передачей данных в качестве параметров
        cur.execute(query, (user_id, user_firstname, user_lastname, user_last_message, is_admin_banned))
        # сохраняем изменения в базе данных
        self.conn.commit()
        # закрываем курсор
        cur.close()

    def update_last_message(self, user_id):
        # создаем курсор для выполнения запросов
        cur = self.conn.cursor()
        # формируем запрос на обновление времени отправки сообщения в таблице
        query = f"""
            UPDATE users 
            SET user_last_message = CURRENT_TIMESTAMP
            WHERE user_id = %s;
        """
        # выполняем запрос с передачей данных в качестве параметра
        cur.execute(query, (user_id,))
        # сохраняем изменения в базе данных
        self.conn.commit()
        # закрываем курсор
        cur.close()

    def toggle_ban_status(self, user_id):
        # создаем курсор для выполнения запросов
        cur = self.conn.cursor()
        # формируем запрос на изменение статуса бана в таблице
        query = f"""
            UPDATE users 
            SET is_admin_banned = NOT is_admin_banned
            WHERE user_id = %s;
        """
        # выполняем запрос с передачей данных в качестве параметра
        cur.execute(query, (user_id,))
        # сохраняем изменения в базе данных
        self.conn.commit()
        # закрываем курсор
        cur.close()
    
    def check_ban_status(self, user_id):
        # создаем курсор для выполнения запросов
        cur = self.conn.cursor()
        # формируем запрос на выборку значения из столбца is_admin_banned по заданному user_id
        query = f"""
            SELECT is_admin_banned 
            FROM users 
            WHERE user_id = %s;
        """
        # выполняем запрос с передачей данных в качестве параметра
        cur.execute(query, (user_id,))
        # получаем результат запроса в виде кортежа
        result = cur.fetchone()
        # закрываем курсор
        cur.close()
        # если результат не пустой, то возвращаем значение из столбца is_admin_banned в виде логического типа
        if result:
            return bool(result[0])
        # иначе возвращаем None
        else:
            return False


