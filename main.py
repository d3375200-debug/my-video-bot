import os, telebot, subprocess, glob
from yt_dlp import YoutubeDL

TOKEN = "8559664636:AAGPh7u2OqwueND1OxygwIybkKl8LQBzE8Y"
bot = telebot.TeleBot(TOKEN)

def split_video(input_file):
    base_name = os.path.splitext(input_file)[0]
    output_pattern = f"{base_name}_part_%03d.mp4"
    subprocess.run(['ffmpeg', '-i', input_file, '-c', 'copy', '-map', '0', '-segment_time', '420', '-f', 'segment', output_pattern])
    return sorted(glob.glob(f"{base_name}_part_*.mp4"))

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "/start":
        return bot.send_message(message.chat.id, "Бот готов! Пришли название или ссылку.")
    s = bot.reply_to(message, "⏳ Качаю...")
    try:
        ydl_opts = {'format': 'best[ext=mp4]/best', 'outtmpl': '%(title)s.%(ext)s', 'restrictfilenames': True, 'default_search': 'ytsearch1', 'noplaylist': True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(message.text, download=True)
            fname = ydl.prepare_filename(info)
        if os.path.getsize(fname) / (1024*1024) > 49:
            bot.edit_message_text("📦 Нарезаю по 7 минут...", message.chat.id, s.message_id)
            for p in split_video(fname):
                with open(p, 'rb') as f: bot.send_document(message.chat.id, f, caption=os.path.basename(p))
                os.remove(p)
        else:
            with open(fname, 'rb') as f: bot.send_document(message.chat.id, f)
        if os.path.exists(fname): os.remove(fname)
    except Exception as e: bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")

bot.infinity_polling()
