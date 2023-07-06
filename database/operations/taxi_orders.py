from .based_class import BaseDB

class TaxiOrder(BaseDB):
    # Метод для добавления нового заказа в таблицу
    def add_order(self, user_id, order_time, order_from, order_to, phone_number):
        # Формируем SQL-запрос для вставки данных
        sql = """
            INSERT INTO taxi_orders (user_id, order_time, order_from, order_to, phone_number)
            VALUES (%s, %s, %s, %s, %s)
        """
        # Выполняем запрос с передачей параметров
        self.cur.execute(sql, (user_id, order_time, order_from, order_to, phone_number))
        # Сохраняем изменения в базе данных
        self.conn.commit()

    # Метод для получения количества заказов в таблице
    def get_order_count(self):
        # Формируем SQL-запрос для подсчета записей
        sql = "SELECT COUNT(*) FROM taxi_orders"
        # Выполняем запрос и получаем результат
        self.cur.execute(sql)
        count = self.cur.fetchone()[0]
        # Возвращаем количество заказов
        return count

    # Метод для получения последнего заказа в таблице
    def get_last_order(self):
        # Формируем SQL-запрос для выборки последней записи по порядку id
        sql = "SELECT * FROM taxi_orders ORDER BY order_id DESC LIMIT 1"
        # Выполняем запрос и получаем результат
        self.cur.execute(sql)
        order = self.cur.fetchone()
        # Возвращаем последний заказ в виде словаря
        if order: 
            return {
                "order_id": order[0],
                "user_id": order[1],
                "order_time": order[2],
                "order_from": order[3],
                "order_to": order[4],
                "phone_number": order[5]
                }
        return None

    # Добавляем параметр offset в метод get_orders
    def get_orders(self, limit, offset):
        # Формируем SQL-запрос для выборки записей по порядку id с ограничением количества и смещением
        sql = "SELECT * FROM taxi_orders ORDER BY order_id DESC LIMIT %s OFFSET %s"
        # Выполняем запрос с передачей параметров и получаем результат
        self.cur.execute(sql, (limit, offset))
        orders = self.cur.fetchall()
        # Возвращаем список заказов в виде словарей
        if orders:
            return [
                {
                    "order_id": order[0],
                    "user_id": order[1],
                    "order_time": order[2],
                    "order_from": order[3],
                    "order_to": order[4],
                    "phone_number": order[5]
                }
                for order in orders
            ]
        return None