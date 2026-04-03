import os
import telebot
import subprocess
import glob
from yt_dlp import YoutubeDL

# Твой токен
TOKEN = "8559664636:AAHAA1S2x-B4msBYxSZ1rU7B93csnmDy7Ls"
bot = telebot.TeleBot(TOKEN)

def split_video(input_file):
    """Режет видео на части по 7 минут (420 секунд)"""
    base_name = os.path.splitext(input_file)[0]
    output_pattern = f"{base_name}_part_%03d.mp4"
    
    # Быстрая нарезка без потери качества
    subprocess.run([
        'ffmpeg', '-i', input_file, '-c', 'copy', '-map', '0', 
        '-segment_time', '420', '-f', 'segment', output_pattern
    ])
    return sorted(glob.glob(f"{base_name}_part_*.mp4"))

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text
    chat_id = message.chat.id
    
    if query == "/start":
        bot.send_message(chat_id, "Пришли название видео или ссылку на YouTube!")
        return

    status_msg = bot.reply_to(message, f"⏳ Ищу и скачиваю...")

    try:
        ydl_opts = {
            'format': 'best[ext=mp4]/best', 
            'outtmpl': '%(title)s.%(ext)s', 
            'restrictfilenames': True,
            'default_search': 'ytsearch1',
            'noplaylist': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            filename = ydl.prepare_filename(info)
        
        file_size = os.path.getsize(filename) / (1024 * 1024)

        if file_size > 49:
            bot.edit_message_text("📦 Нарезаю по 7 минут...", chat_id, status_msg.message_id)
            parts = split_video(filename)
            for part in parts:
                with open(part, 'rb') as f:
                    bot.send_document(chat_id, f, caption=os.path.basename(part))
                os.remove(part)
        else:
            with open(filename, 'rb') as f:
                bot.send_document(chat_id, f, caption=os.path.basename(filename))

        if os.path.exists(filename):
            os.remove(filename)
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка: {str(e)}")

bot.infinity_polling() 
