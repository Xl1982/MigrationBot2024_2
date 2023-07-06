import requests

from source.config import WEATHER_API


# Задаем базовый URL для API openweather
base_url = "http://api.openweathermap.org/data/2.5/weather?"

# Функция для получения данных о погоде по названию города
def get_weather_by_city(city):
  # Формируем полный URL с параметрами запроса
  full_url = base_url + f"q={city}&units=metric&appid={WEATHER_API}"
  # Отправляем запрос и получаем ответ в формате JSON
  response = requests.get(full_url).json()
  # Проверяем статус ответа
  if response["cod"] == 200:
    # Извлекаем нужные данные из ответа
    temp = response["main"]["temp"] # температура в Цельсиях
    feels_like = response["main"]["feels_like"] # ощущаемая температура в Цельсиях
    pressure = response["main"]["pressure"] # давление в гПа
    humidity = response["main"]["humidity"] # влажность в %
    wind_speed = response["wind"]["speed"] # скорость ветра в м/с
    wind_deg = response["wind"]["deg"] # угол направления ветра в градусах
    clouds = response["clouds"]["all"] # процент облачности
    main = response["weather"][0]["main"] # общее название погодного явления
    icon = response["weather"][0]["icon"] # иконка погоды
    sunrise = response["sys"]["sunrise"] # время восхода солнца в UNIX формате
    sunset = response["sys"]["sunset"] # время захода солнца в UNIX формате
    # Возвращаем данные в виде словаря
    return {
      "city": city,
      "temp": temp,
      "feels_like": feels_like,
      "pressure": pressure,
      "humidity": humidity,
      "wind_speed": wind_speed,
      "wind_deg": wind_deg,
      "clouds": clouds,
      "main": main,
      "icon": icon,
      "sunrise": sunrise,
      "sunset": sunset
    }
  else:
    # Возвращаем сообщение об ошибке
    return {
      "error": response["message"]
    }


# Функция для формирования пожелания хорошего дня по названию погодного явления
def get_wish(main):
  # Создаем словарь с пожеланиями для разных погодных явлений
  wishes = {
    "Clear": "Желаю тебе солнечного настроения!",
    "Clouds": "Пусть тучи не затмевают твой свет!",
    "Rain": "Не промокни!",
    "Snow": "Снеговиков не забудь слепить!",
    "Thunderstorm": "Будь осторожен на улице!",
    "Drizzle": "Не забудь зонт!",
    "Mist": "Остерегайся туманных существ!",
    "Smoke": "Дыши полной грудью!",
    "Haze": "Не заблудись в дымке!",
    "Dust": "Пыль не лучший аксессуар!",
    "Fog": "Не теряйся в тумане!",
    "Sand": "Песок - это не только на пляже!",
    "Ash": "Вулканы не шутят!",
    "Squall": "Держись крепче!",
    "Tornado": "Укройся в безопасном месте!"
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