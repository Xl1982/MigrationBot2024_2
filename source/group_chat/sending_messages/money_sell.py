# Подробное объяснение кода:

# Импорт необходимых модулей
import datetime  # Модуль для работы с датой и временем
import requests  # Модуль для выполнения HTTP-запросов
import pytz  # Модуль для работы с часовыми поясами


from source.config import EXCHANGE_TOKEN

# Установка API-ключа
# api_key_exchange = "80730760f799bc84a6bc9a06"

# Описание класса CurrencyConverter
class MoneySellConverter:
    # Конструктор класса
    def __init__(self, api_key=EXCHANGE_TOKEN):
        # Инициализация переменных
        self.api_key = api_key
        self.timezone = pytz.timezone('Europe/Madrid')  # Установка часового пояса на 'Europe/Madrid'
        self.days_of_week = {  # Словарь, соотносящий номер дня недели с его названием
            0: 'Понедельник',
            1: 'Вторник',
            2: 'Среда',
            3: 'Четверг',
            4: 'Пятница',
            5: 'Суббота',
            6: 'Воскресенье'
        }
        self.money_sell_text = None  # Переменная для хранения текста с обменным курсом
        self.usd_rate = None  # Переменная для хранения курса USD
        self.rub_rate = None  # Переменная для хранения курса RUB
        self.uah_rate = None  # Переменная для хранения курса UAH

    # Метод для получения текущей даты и времени
    def get_current_datetime(self):
        now = datetime.datetime.now(self.timezone)  # Получение текущей даты и времени в указанном часовом поясе
        day_of_week = now.weekday()  # Получение номера дня недели (0 - понедельник, 1 - вторник и т.д.)
        formatted_datetime = now.strftime(f"{self.days_of_week[day_of_week]}, %d-%m-%Y, %H:%M")  # Форматирование даты и времени в строку
        return formatted_datetime  # Возвращение отформатированной даты и времени

    # Метод для получения курсов валют
    def get_exchange_rates(self):
        url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/EUR"  # URL для получения текущего курса валют
        response = requests.get(url)  # Выполнение GET-запроса к указанному URL
        data = response.json()  # Извлечение данных из ответа в формате JSON
        return data.get("conversion_rates")  # Возвращение курсов валют из данных

    # Метод для конвертации валюты с учетом коэффициента маржи
    def convert_currency(self, margin_coefficient):
        formatted_datetime = self.get_current_datetime()  # Получение отформатированной даты и времени
        exchange_rates = self.get_exchange_rates()  # Получение курсов валют

        # Проверка наличия данных о конверсии валют
        if exchange_rates is None:
            print("Отсутствуют данные о конверсии валют.")
            return

        # Проверка наличия всех требуемых курсов валют
        if "USD" not in exchange_rates or "RUB" not in exchange_rates or "UAH" not in exchange_rates:
            print("Один из курсов валют (USD, RUB, UAH) отсутствует в ответе.")
            return

        # Получение курсов валют
        self.usd_rate = exchange_rates["USD"]
        self.rub_rate = exchange_rates["RUB"]
        self.uah_rate = exchange_rates["UAH"]

        # Вычисление конверсии с учетом коэффициента маржи
        eur_to_usd = 1 / (self.usd_rate * margin_coefficient)
        eur_to_rub = 1 / (self.rub_rate * margin_coefficient)
        eur_to_uah = 1 / (self.uah_rate * margin_coefficient)
        usd_to_eur = 1 / eur_to_usd
        rub_to_eur = 1 / eur_to_rub
        uah_to_eur = 1 / eur_to_uah

        # Формирование текста с обменным курсом
        self.money_sell_text = (
            f"Срочно купим за Евро рубли и гривны\n"
            f"Цена на {formatted_datetime}\n"
            f"💶 За 1 🇪🇺EUR купим: {rub_to_eur:.2f} 🇷🇺RUB\n"
            f"💶 За 1 🇪🇺EUR купим: {uah_to_eur:.2f} 🇺🇦UAH\n"
        )

        return self.money_sell_text, self.usd_rate, self.rub_rate, self.uah_rate

class CurrencyConverter:
    def __init__(self, api_key=EXCHANGE_TOKEN):
        self.api_key = api_key
        self.timezone = pytz.timezone('Europe/Madrid')
        self.days_of_week = {
            0: 'Понедельник',
            1: 'Вторник',
            2: 'Среда',
            3: 'Четверг',
            4: 'Пятница',
            5: 'Суббота',
            6: 'Воскресенье'
        }
        self.exchange_text = None
        self.usd_rate = None
        self.rub_rate = None
        self.uah_rate = None

    def get_current_datetime(self):
        now = datetime.datetime.now(self.timezone)
        day_of_week = now.weekday()
        formatted_datetime = now.strftime(f"{self.days_of_week[day_of_week]}, %d-%m-%Y, %H:%M")
        return formatted_datetime

    def get_exchange_rates(self):
        url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/EUR"
        response = requests.get(url)
        data = response.json()
        return data.get("conversion_rates")

    def convert_currency(self):
        formatted_datetime = self.get_current_datetime()
        exchange_rates = self.get_exchange_rates()

        if exchange_rates is None:
            print("Отсутствуют данные о конверсии валют.")
            return

        if "USD" not in exchange_rates or "RUB" not in exchange_rates or "UAH" not in exchange_rates:
            print("Один из курсов валют (USD, RUB, UAH) отсутствует в ответе.")
            return

        self.usd_rate = exchange_rates["USD"]
        self.rub_rate = exchange_rates["RUB"]
        self.uah_rate = exchange_rates["UAH"]

        eur_to_usd = 1 / self.usd_rate
        eur_to_rub = 1 / self.rub_rate
        eur_to_uah = 1 / self.uah_rate
        usd_to_eur = 1 / eur_to_usd
        rub_to_eur = 1 / eur_to_rub
        uah_to_eur = 1 / eur_to_uah

        self.exchange_text = (f"Курс 🇪🇺EUR на {formatted_datetime}\n"
            f"💶 Чтобы купить 1 🇪🇺EUR, нужно отдать: {usd_to_eur:.2f} 🇺🇸USD\n"
            f"💶 Чтобы купить 1 🇪🇺EUR, нужно отдать: {rub_to_eur:.2f} 🇷🇺RUB\n"
            f"💶 Чтобы купить 1 🇪🇺EUR, нужно отдать: {uah_to_eur:.2f} 🇺🇦UAH\n")

        return self.exchange_text, self.usd_rate, self.rub_rate, self.uah_rate

# Использование класса
api_key_exchange = "80730760f799bc84a6bc9a06"
converter = CurrencyConverter(api_key_exchange)
exchange_text, usd_rate, rub_rate, uah_rate = converter.convert_currency()