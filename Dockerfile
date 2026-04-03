FROM python:3.10

# Устанавливаем инструменты для работы с видео
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY . .

# Устанавливаем библиотеки бота
RUN pip install --no-cache-dir pyTelegramBotAPI yt-dlp

# Запуск программы
CMD ["python", "main.py"]
