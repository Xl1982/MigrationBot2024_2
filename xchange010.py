import datetime
import requests
import pytz

class CurrencyConverter:
    def __init__(self, api_key):
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

# Пример использования полученных данных

