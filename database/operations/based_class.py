import psycopg2

class BaseDB:
    def __init__(self):
        self.conn = psycopg2.connect("dbname='telegram_database' user='postgres' password='postgres' host='localhost' port='5432'")
        self.cur = self.conn.cursor()
    
    def __del__(self):
        self.conn.close()