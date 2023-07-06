import requests

from datetime import datetime, timedelta

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

def get_weather_forecast(target_date, target_time, city_name='Torrevieja'):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city_name,
        "appid": WEATHER_API,
        "units": "metric"
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
                "wind_direction_deg": forecast["wind"]["deg"],  # Добавлен угол направления ветра
                "wind_direction": get_wind_direction(forecast["wind"]["deg"]),  # Добавлено название стороны света
                "sunrise": datetime.fromtimestamp(city_data["sunrise"]).time(),
                "sunset": datetime.fromtimestamp(city_data["sunset"]).time(),
                "city_name": city_data["name"] 
            }

            main_weather = forecast.get("weather")[0].get("main")
            wish = get_wish(main_weather)
            forecast_info["wish"] = wish

            forecast_data.append(forecast_info)

    return forecast_data