# Импортируем библиотеку psycopg2
import psycopg2



try:
    conn = psycopg2.connect(
        host="localhost",
        database='telegram_database',
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()
    # Создаем таблицу users, если она еще не существует
    # уникальный серийный ID для каждого пользователя
    # уникальный идентификатор пользователя
    # имя пользователя
    # фамилия пользователя
    # время последнего сообщения в беседе
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL, 
            user_id BIGINT PRIMARY KEY, 
            user_firstname VARCHAR(255) NOT NULL, 
            user_lastname VARCHAR(255), 
            user_last_message TIMESTAMP, 
            is_admin_banned BOOLEAN 
        )
    """)

    # Создаем таблицу taxi_orders, если она еще не существует
    # уникальный идентификатор заказа
    # идентификатор пользователя, который заказал такси (связан с таблицей users)
    # время заказа
    # место, откуда заказано такси
    # место, куда заказано такси
    # номер телефона пользователя
    # флаг, запрещен ли пользователь писать через бота в лс

    cur.execute("""
        CREATE TABLE IF NOT EXISTS taxi_orders (
            order_id SERIAL PRIMARY KEY, 
            user_id BIGINT REFERENCES users(user_id), 
            order_time TIMESTAMP NOT NULL, 
            order_from VARCHAR(255) NOT NULL, 
            order_to VARCHAR(255) NOT NULL, 
            phone_number VARCHAR(20) NOT NULL 
        )
    """)

    # Создаем таблицу translator_orders, если она еще не существует
    # уникальный идентификатор заказа
    # идентификатор пользователя, который заказал переводчика (связан с таблицей users)
    # время заказа
    # место встречи с переводчиком
    # номер телефона пользователя
    cur.execute("""
        CREATE TABLE IF NOT EXISTS translator_orders ( 
            order_id SERIAL PRIMARY KEY, 
            user_id BIGINT REFERENCES users(user_id),
            order_time TIMESTAMP NOT NULL, 
            meeting_place VARCHAR(255) NOT NULL, 
            phone_number VARCHAR(20) NOT NULL 
        )
    """)

    # Создаем таблицу groups, если она еще не существует
    # this will create a unique ID for each group
    # уникальный идентификатор чата, в котором есть бот
    # время таймаута в секундах для сообщений в чате (не больше года)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id SERIAL, 
            chat_id BIGINT PRIMARY KEY, 
            timeout INT CHECK (timeout > 0 AND timeout <= 31536000) 
        )
    """)


    cur.execute('CREATE TABLE IF NOT EXISTS products (idx text PRIMARY KEY, title text, body text, photo bytea, price real, tag text)')
    cur.execute('CREATE TABLE IF NOT EXISTS orders (order_id SERIAL PRIMARY KEY, cid BIGINT, usr_name text, usr_address text, products text, sending BOOLEAN DEFAULT false)')
    cur.execute('CREATE TABLE IF NOT EXISTS cart (cid BIGINT, idx text REFERENCES products (idx), quantity int)')
    cur.execute('CREATE TABLE IF NOT EXISTS categories (idx text PRIMARY KEY, title text)')
    cur.execute('CREATE TABLE IF NOT EXISTS wallet (cid BIGINT, balance real)')
    cur.execute('CREATE TABLE IF NOT EXISTS questions (cid BIGINT, question text)')


    # Сохраняем изменения в базе данных
    conn.commit()

    # Закрываем соединение и курсор
    cur.close()
    conn.close()

    print('База данных успешно создана')
except Exception as e:
    print(f'В процессе создания базы данных произошла ошибка: {e}') 