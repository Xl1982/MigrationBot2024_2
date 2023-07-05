import yt_dlp
import re

from source.bot_init import dp, bot

MAX_FILE_SIZE_MB = 50
ADMIN_ID = 1387633357

# #  Функция для обновления прогресса загрузки или конвертации
# async def update_progress(data, chat_id, message_id):
#     if data['status'] == 'downloading': # Если идет загрузка
#         percent = data['_percent_str'] # Процент загрузки в виде строки
#         speed = data['_speed_str'] # Скорость загрузки в виде строки
#         await bot.edit_message_text(f"Загружается {percent} со скоростью {speed}", chat_id, message_id) # Редактируем сообщение с прогрессом (нужно сохранить message_id при первом выводе)
#     elif data['status'] == 'finished': # Если загрузка завершена
#         await bot.edit_message_text("Загрузка завершена, идет конвертация...", chat_id, message_id) # Редактируем сообщение с прогрессом


# Функция для загрузки и отправки музыки по ссылке
async def download_music(url):
    # Проверяем размер аудиофайла по ссылке
    error = await check_audio_size(url)
    if error is None:
        # Загружаем аудиофайл по ссылке
        audio_file_path = await download_audio(url)
        if audio_file_path.startswith('Произошла ошибка'):
            # Возвращаем ошибку при загрузке
            return audio_file_path
        else:
            # Возвращаем аудиофайл
            return audio_file_path
    else:
        # Возвращаем ошибку о превышении лимита размера
        return error

# Функция для проверки ссылки на видео
async def check_video_url(video_url):
    if not video_url:
        return 'Это не ссылка.'
    else:
        return None


# Функция для проверки размера аудиофайла по ссылке
async def check_audio_size(video_url):
    try:
        # Создаем объект yt_dlp с опцией для получения информации о видео
        ydl_opts = {
            'format': 'bestaudio/best',  # Выбираем лучший аудиопоток
            'skip_download': True,  # Не загружаем видео, только получаем информацию
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # Создаем контекстный менеджер для yt_dlp
            info_dict = ydl.extract_info(video_url)  # Получаем информацию о видео
            audio_file_size = info_dict.get('filesize', None) 
            if audio_file_size is None:  # Если размер не указан, то пробуем вычислить его по битрейту и длительности
                audio_file_size = info_dict.get('abr', None) * info_dict.get('duration', None) / (8 * 1024)  # Размер в МБ
            else:
                audio_file_size = audio_file_size / (1024 * 1024)  # Размер аудиопотока в МБ
    except Exception as e:  # Обрабатываем возможные исключения
        return f'Произошла ошибка при проверке размера аудио: {str(e)}'

    if audio_file_size > MAX_FILE_SIZE_MB:  # Если размер превышает лимит, то не загружаем файл
        return 'Размер аудиофайла превышает 50 МБ. Невозможно загрузить.'
    else:
        return None


# Функция для загрузки аудиофайла по ссылке
async def download_audio(video_url):
    try:
        # Создаем объект yt_dlp с опциями для загрузки и конвертации аудио
        ydl_opts = {
            'format': 'bestaudio/best',  # Выбираем лучший аудиопоток
            'outtmpl': '%(title)s.%(ext)s',  # Устанавливаем шаблон для имени файла с названием видео
            'postprocessors': [{  # Добавляем постобработчик для извлечения аудио из видео
                'key': 'FFmpegExtractAudio',  # Используем ffmpeg для конвертации
                'preferredcodec': 'mp3',  # Выбираем формат mp3 для аудиофайла
                'preferredquality': '192',  # Выбираем качество 192 кбит/с
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # Создаем контекстный менеджер для yt_dlp
            ydl.download([video_url])  # Загружаем видео по ссылке
            info_dict = ydl.extract_info(video_url, download=False)  # Получаем информацию о видео
            video_title = info_dict.get('title', None)  # Получаем название видео
            audio_file_path = f'{video_title}.mp3'  # Формируем путь к загруженному аудио с названием видео
    except Exception as e:  # Обрабатываем возможные исключения
        return f'Произошла ошибка при загрузке аудио: {str(e)}'

    return audio_file_path


# Функция для проверки размера видеофайла по ссылке
async def check_video_size(video_url):
    try:
        # Создаем объект yt_dlp с опцией для получения информации о видео
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Выбираем лучший видеопоток и аудиопоток и объединяем их
            'skip_download': True,  # Не загружаем видео, только получаем информацию
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # Создаем контекстный менеджер для yt_dlp
            info_dict = ydl.extract_info(video_url)  # Получаем информацию о видео
            video_file_size = info_dict.get('filesize', None) 
            if video_file_size is None:  # Если размер не указан, то пробуем вычислить его по битрейту и длительности
                video_file_size = info_dict.get('vbr', None) * info_dict.get('duration', None) / (8 * 1024)  # Размер в МБ
            else:
                video_file_size = video_file_size / (1024 * 1024)  # Размер видеопотока в МБ
    except Exception as e:  # Обрабатываем возможные исключения
        return f'Произошла ошибка при проверке размера видео: {str(e)}'

    if video_file_size > MAX_FILE_SIZE_MB:  # Если размер превышает лимит, то не загружаем файл
        return 'Размер видеофайла превышает 50 МБ. Невозможно загрузить.'
    else:
        return None


# Функция для загрузки видеофайла по ссылке
async def download_video(video_url):
    try:
        # Создаем объект yt_dlp с опциями для загрузки и конвертации видео
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Выбираем лучший видеопоток и аудиопоток и объединяем их
            'outtmpl': '%(id)s.%(ext)s',  # Устанавливаем шаблон для имени файла
            'postprocessors': [{  # Добавляем постобработчик для конвертации видео в формат mp4
                'key': 'FFmpegVideoConvertor',  # Используем ffmpeg для конвертации
                'preferedformat': 'mp4',  # Выбираем формат mp4 для видеофайла
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # Создаем контекстный менеджер для yt_dlp
            ydl.download([video_url])  # Загружаем видео по ссылке
            info_dict = ydl.extract_info(video_url, download=False)  # Получаем информацию о видео без загрузки
            video_id = info_dict.get('id', None)  # Получаем идентификатор видео
            video_file_path = f'{video_id}.mp4'  # Формируем путь к загруженному видео
    except Exception as e:  # Обрабатываем возможные исключения
        return f'Произошла ошибка при загрузке видео: {str(e)}'

    return video_file_path


def is_youtube_link(url):
    # Регулярное выражение для проверки, что ссылка принадлежит YouTube
    youtube_pattern = r"(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)"

    # Проверяем, соответствует ли ссылка YouTube
    if re.match(youtube_pattern, url):
        return True
    else:
        return False


def is_youtube_music_link(url):
    # Регулярное выражение для проверки, что ссылка принадлежит YouTube Music
    youtube_music_pattern = r"(?:https?://)?(?:www\.)?(?:music\.youtube\.com)"

    # Проверяем, соответствует ли ссылка YouTube Music
    if re.match(youtube_music_pattern, url):
        return True
    else:
        return False
