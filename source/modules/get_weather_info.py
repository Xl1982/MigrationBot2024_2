import requests

from typing import List, Dict, Union, Optional
from datetime import datetime, timedelta, date, time

from source.config import WEATHER_API


# Функция для формирования пожелания хорошего дня по названию погодного явления
def get_wish(main):
    # Создаем словарь с пожеланиями и соответствующими смайликами
    wishes = {
        "Clear": "Желаю тебе солнечного настроения! ☀️",
        "Clouds": "Пусть тучи не затмевают твой свет! ☁️",
        "Rain": "Не промокни! 🌧️",
        "Snow": "Снеговиков не забудь слепить! ❄️",
        "Thunderstorm": "Будь осторожен на улице! ⛈️",
        "Drizzle": "Не забудь зонт! 🌦️",
        "Mist": "Остерегайся туманных существ! 🌫️",
        "Smoke": "Дыши полной грудью! 🌫️",
        "Haze": "Не заблудись в дымке! 🌫️",
        "Dust": "Пыль не лучший аксессуар! 💨",
        "Fog": "Не теряйся в тумане! 🌫️",
        "Sand": "Песок - это не только на пляже! 🏖️",
        "Ash": "Вулканы не шутят! 🌋",
        "Squall": "Держись крепче! 🌬️",
        "Tornado": "Укройся в безопасном месте! 🌪️"
    }
    # Возвращаем пожелание по ключу или дефолтное пожелание
    return wishes.get(main, "Желаю тебе хорошего дня!")


# Функция для перевода угла направления ветра в название стороны света
def get_wind_direction(deg):
    # Создаем список с названиями сторон света
    directions = ["Северный", "Северо-восточный", "Восточный", "Юго-восточный", "Южный", "Юго-западный", "Западный", "Северо-западный"]
    # Определяем индекс стороны света по углу
    index = round(deg / 45) % 8
    # Возвращаем название стороны света
    return directions[index]

def get_weather_forecast(target_date: date, target_time: time, city_name: str = 'Torrevieja') -> List[Dict[str, Union[date, time, float, int, Optional[int], str, int]]]:
    """
    Получает прогноз погоды для заданного местоположения и времени.

    Параметры:
        - target_date (date): Целевая дата прогноза погоды.
        - target_time (time): Целевое время прогноза погоды.
        - city_name (str): Название города (по умолчанию 'Torrevieja').

    Возвращает:
        Список словарей, содержащих информацию о прогнозе погоды для указанного местоположения и времени.
        Каждый словарь в списке имеет следующие ключи:
            - "date" (date): Дата прогноза погоды.
            - "time" (time): Время прогноза погоды.
            - "temperature" (float): Текущая температура.
            - "max_temperature" (float): Максимальная температура.
            - "min_temperature" (float): Минимальная температура.
            - "humidity" (int): Влажность воздуха (в процентах).
            - "pressure" (int): Атмосферное давление (в гектопаскалях).
            - "visibility" (Optional[int]): Видимость (в метрах), может быть None.
            - "wind_speed" (float): Скорость ветра (в м/с).
            - "wind_direction_deg" (int): Угол направления ветра в градусах.
            - "wind_direction" (str): Название стороны света, откуда дует ветер.
            - "sunrise" (time): Время восхода солнца.
            - "sunset" (time): Время заката солнца.
            - "city_name" (str): Название города.
            - "description" (str): Описание погоды.
            - "cloudiness" (int): Облачность (в процентах).

    Примечания:
        - Для получения прогноза погоды используется OpenWeatherMap API.
        - Для работы функции требуется наличие действующего ключа API (WEATHER_API).
        - Возвращается список словарей, так как прогноз погоды может быть доступен на разные периоды времени в указанную дату и время.
        - Если для указанной даты и времени нет доступного прогноза погоды, возвращается пустой список.

    Пример использования:
        target_date = date(2023, 7, 7)
        target_time = time(8, 50)
        forecast = get_weather_forecast(target_date, target_time, city_name='Torrevieja')
        for info in forecast:
            print(f"Дата: {info['date']}, Время: {info['time']}, Температура: {info['temperature']}, Описание погоды: {info['description']}")
    """
    # Описание погоды и облачность для кодов прогноза OpenWeatherMap
    weather_codes = {
        "01": "Ясно",
        "02": "Малооблачно",
        "03": "Облачно с прояснениями",
        "04": "Облачно",
        "09": "Ливень",
        "10": "Дождь",
        "11": "Гроза",
        "13": "Снег",
        "50": "Туман"
    }

    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city_name,
        "appid": WEATHER_API,
        "units": "metric",
        "lang": "ru"
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    forecast_data = []
    city_data = data["city"]
    for forecast in data["list"]:
        forecast_datetime = datetime.fromtimestamp(forecast["dt"])
        forecast_date = forecast_datetime.date()
        forecast_time = forecast_datetime.time()
        if forecast_date == target_date and forecast_time == target_time:
            forecast_info = {
                "date": forecast_date,
                "time": forecast_time,
                "temperature": forecast["main"]["temp"],
                "max_temperature": forecast["main"]["temp_max"],
                "min_temperature": forecast["main"]["temp_min"],
                "humidity": forecast["main"]["humidity"],
                "pressure": forecast["main"]["pressure"],
                "visibility": forecast.get("visibility"),
                "wind_speed": forecast["wind"]["speed"],
                "wind_direction_deg": forecast["wind"]["deg"],
                "wind_direction": get_wind_direction(forecast["wind"]["deg"]),
                "sunrise": datetime.fromtimestamp(city_data["sunrise"]).time(),
                "sunset": datetime.fromtimestamp(city_data["sunset"]).time(),
                "city_name": city_data["name"],
                "description": weather_codes.get(forecast["weather"][0]["icon"][:2]),
                "cloudiness": forecast["clouds"]["all"]
            }

            forecast_data.append(forecast_info)

    return forecast_data