from .based_class import BaseDB

class TranslatorOrder(BaseDB):
    def get_order_count(self):
        self.cur.execute("SELECT COUNT(*) FROM translator_orders")
        count = self.cur.fetchone()[0]
        return count

    def get_latest_order(self):
        self.cur.execute("SELECT * FROM translator_orders ORDER BY order_time DESC LIMIT 1")
        order = self.cur.fetchone()
        return order

    def add_order(self, user_id, order_time, meeting_place, phone_number):
        query = """
            INSERT INTO translator_orders (user_id, order_time, meeting_place, phone_number)
            VALUES (%s, %s, %s, %s)
        """
        values = (user_id, order_time, meeting_place, phone_number)
        self.cur.execute(query, values)
        self.conn.commit()

    def get_orders(self, limit, offset=0):
        query = """
            SELECT * FROM translator_orders
            ORDER BY order_time DESC
            LIMIT %s OFFSET %s
        """
        self.cur.execute(query, (limit, offset))
        orders = self.cur.fetchall()
        return orders