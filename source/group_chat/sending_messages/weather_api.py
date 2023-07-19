import requests
import datetime

class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'http://api.openweathermap.org/data/2.5/weather'

    def get_weather(self, city):
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        response = requests.get(self.base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            cur_weather = data['main']['temp']
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            wind_speed = data['wind']['speed']
            wind_direction = data['wind']['deg']
            cloudiness = data['clouds']['all']
            sunrise = datetime.datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
            sunset = datetime.datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')

            if 'rain' in data:
                rain_volume = data['rain']['1h'] if '1h' in data['rain'] else data['rain']['3h']
                weather_text = f'🌍 ***{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}***\n' \
                               f'🌤️ Погода в городе {city}:\n' \
                               f'🌡️ Температура воздуха: {cur_weather}°C\n' \
                               f'💧 Влажность: {humidity}%\n' \
                               f'🌬️ Давление: {pressure} мм.рт.ст\n' \
                               f'💨 Скорость ветра: {wind_speed} м/c\n' \
                               f'🧭 Направление ветра: {wind_direction}°\n' \
                               f'☁️ Облачность: {cloudiness}%\n' \
                               f'🌧️ Количество осадков: {rain_volume} мм/ч\n' \
                               f'🌅 Время восхода солнца: {sunrise}\n' \
                               f'🌇 Время заката солнца: {sunset}\n' \
                               f'🌞 Хорошего дня!'
            else:
                weather_text = f'🌍 ***{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}***\n' \
                               f'🌤️ Погода в городе {city}:\n' \
                               f'🌡️ Температура воздуха: {cur_weather}°C\n' \
                               f'💧 Влажность: {humidity}%\n' \
                               f'🌬️ Давление: {pressure} мм.рт.ст\n' \
                               f'💨 Скорость ветра: {wind_speed} м/c\n' \
                               f'🧭 Направление ветра: {wind_direction}°\n' \
                               f'☁️ Облачность: {cloudiness}%\n' \
                               f'🌅 Время восхода солнца: {sunrise}\n' \
                               f'🌇 Время заката солнца: {sunset}\n' \
                               f'🌞 Хорошего дня!'

            return weather_text
        else:
            return '❌ Не удалось получить данные о погоде'