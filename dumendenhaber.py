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
no_news_count = 0  # Yeni haber bulunamadığında kaç kez kontrol yapıldığını sayar

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
    global notified_news, no_news_count
    print("Haberler kontrol ediliyor...")
    
    latest_news = fetch_latest_news()
    if not latest_news:
        no_news_count += 1
        if no_news_count <= 2:  # İlk iki "Yeni haber yok" mesajını gönder
            message = "Yeni bir haber bulunamadı."
            print(message)
            await send_telegram_message(message)
        elif no_news_count > 2:  # 2 defadan sonra mesaj göndermeyi durdur
            print("Yeni haber yok. Daha fazla mesaj gönderilmeyecek.")
        return

    title, link = latest_news
    if title not in notified_news:  # Eğer yeni bir haber varsa
        message = f"Yeni Haber:\nBaşlık: {title}\nBağlantı: {link}"
        print(f"Gönderilecek mesaj: {message}")
        await send_telegram_message(message)
        notified_news.add(title)
        no_news_count = 0  # Yeni haber bulunduğunda sayacı sıfırla
        print(f"Bildirim gönderildi: {title}")
    else:
        print(f"Kontrol edilen haber zaten bildirildi: {title}")

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

