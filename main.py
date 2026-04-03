import os
import telebot
import subprocess
import glob
from yt_dlp import YoutubeDL

# ТВОЙ ТОКЕН
TOKEN = "8559664636:AAGPh7u2OqwueND1OxygwIybkKl8LQBzE8Y"
bot = telebot.TeleBot(TOKEN)

def split_video(input_file):
    """Режет видео на части по 7 минут для обхода лимита 50МБ"""
    base_name = os.path.splitext(input_file)[0]
    output_pattern = f"{base_name}_part_%03d.mp4"
    subprocess.run([
        'ffmpeg', '-i', input_file, '-c', 'copy', '-map', '0', 
        '-segment_time', '420', '-f', 'segment', output_pattern
    ])
    return sorted(glob.glob(f"{base_name}_part_*.mp4"))

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "/start":
        return bot.send_message(message.chat.id, "Бот обновлен! Пришли ссылку на видео или его название.")
    
    status = bot.reply_to(message, "⏳ Ищу видео (использую обход блокировок)...")
    
    try:
        # Улучшенные настройки для обхода защиты YouTube
        ydl_opts = {
            'format': 'best[ext=mp4]/best', 
            'outtmpl': '%(title)s.%(ext)s',
            'restrictfilenames': True,
            'default_search': 'ytsearch1',
            'noplaylist': True,
            # Маскируемся под обычный браузер Chrome на Windows
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'referer': 'https://www.google.com/',
   
            'quiet': True,
            'no_warnings': True,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(message.text, download=True)
            filename = ydl.prepare_filename(info)
        
        file_size = os.path.getsize(filename) / (1024 * 1024)

        if file_size > 48: # Оставляем запас до 50МБ
            bot.edit_message_text(f"📦 Файл весит {int(file_size)}МБ. Нарезаю...", message.chat.id, status.message_id)
            parts = split_video(filename)
            for part in parts:
                with open(part, 'rb') as f:
                    bot.send_document(message.chat.id, f, caption=os.path.basename(part))
                os.remove(part)
        else:
            with open(filename, 'rb') as f:
                bot.send_document(message.chat.id, f, caption=os.path.basename(filename))
        
        if os.path.exists(filename):
            os.remove(filename)
            
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}\n\nПопробуй другую ссылку или подожди немного.")

if __name__ == "__main__":
    bot.infinity_polling()
