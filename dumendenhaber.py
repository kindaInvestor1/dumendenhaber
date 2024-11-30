import requests
from bs4 import BeautifulSoup
from telegram import Bot
import schedule
import time
import asyncio

# Telegram bot token ve chat ID
BOT_TOKEN = "8045881378:AAHaZ3zlCixKbkanXaRVNpJvoBI7e_GRumQ"
CHAT_ID = "6041080562"

# Daha önce bildirilen haberleri saklamak için bir liste
notified_news = set()

# Haber sitesinden en son haberi çekme fonksiyonu
def fetch_latest_news():
    url = "https://www.bloomberght.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Haber başlığı ve bağlantısını bul
    story = soup.find("a", class_="min-h-16 inline-flex items-center")  # Doğru sınıf adı
    if story:
        title = story.find("span", class_="line-clamp-2").get_text(strip=True)  # Haber başlığı
        link = "https://www.bloomberght.com" + story["href"]  # Haber bağlantısı
        return (title, link)
    return None

# Yeni haberi kontrol edip Telegram'a gönderen fonksiyon
async def check_and_notify():
    global notified_news
    print("Haberler kontrol ediliyor...")
    
    latest_news = fetch_latest_news()
    if not latest_news:
        print("Yeni haber bulunamadı.")
        return
    
    title, link = latest_news
    print(f"Kontrol edilen haber: {title}")
    
    if title not in notified_news:
        message = f"Yeni Haber:\nBaşlık: {title}\nBağlantı: {link}"
        print(f"Gönderilecek mesaj: {message}")
        await send_telegram_message(message)  # Mesaj gönderme işlemi asenkron
        notified_news.add(title)
        print(f"Bildirim gönderildi: {title}")

# Telegram mesajı gönderme fonksiyonu
async def send_telegram_message(message):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message)

# Zamanlayıcı ile periyodik kontrol (asenkron çalıştırma)
def run_scheduler():
    loop = asyncio.get_event_loop()
    while True:
        schedule.run_pending()
        loop.run_until_complete(asyncio.sleep(1))  # Asenkron uyku

# Zamanlayıcıyı yapılandır
schedule.every(1).minutes.do(lambda: asyncio.run(check_and_notify()))

print("Bot çalışıyor. Yeni haberler kontrol ediliyor...")
run_scheduler()
