import requests
import datetime
from source.config import *

class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'http://api.openweathermap.org/data/2.5/forecast/daily'

    def get_weather_forecast(self, city):
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'cnt': 2  # Запрашиваем прогноз на 2 дня (сегодня и следующий день)
        }
        response = requests.get(self.base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            forecast = None
            for item in data['list']:
                dt = datetime.date.fromtimestamp(item['dt'])
                if dt == tomorrow:
                    forecast = item
                    break

            if forecast:
                temperature = forecast['temp']['day']
                humidity = forecast['humidity']
                wind_speed = forecast['speed']
                wind_direction = forecast['deg']
                weather_text = f'🌍 ***{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}***\n' \
                               f'🌤️ Погода в городе {city} на завтрашний день:\n' \
                               f'🌡️ Температура воздуха: {temperature}°C\n' \
                               f'💧 Влажность: {humidity}%\n' \
                               f'💨 Скорость ветра: {wind_speed} м/c\n' \
                               f'🧭 Направление ветра: {wind_direction}°\n' \
                               f'🌞 Хорошего дня!'
            else:
                weather_text = f'❌ Прогноз на завтрашний день не доступен'

            return weather_text
        else:
            return '❌ Не удалось получить данные о погоде'

# Пример использования класса WeatherAPI
api_key = WEATHER_API  # Замените YOUR_API_KEY на ваш собственный ключ API

weather_api = WeatherAPI(api_key)
city = 'Torrevieja'  # Замените на нужный вам город

weather_text = weather_api.get_weather_forecast(city)
print(weather_text)
