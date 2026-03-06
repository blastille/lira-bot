import cloudscraper
import requests
import time
import json
import os
import gc
from datetime import datetime
import pytz

TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
CACHE_FILE = "cache.json"
TZ = pytz.timezone("Asia/Damascus")

def get_rates():
    scraper = cloudscraper.create_scraper()
    response = scraper.get("https://sse.sp-today.com/snapshot")
    data = response.json()
    scraper.close()
    return data["data"]["currencies"]

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(rates):
    with open(CACHE_FILE, "w") as f:
        json.dump(rates, f)

def get_emoji(old, new):
    if old is None:
        return "🆕"
    if new > old:
        return "📈"
    if new < old:
        return "📉"
    return "➡️"

def prices_changed(current, cached):
    keys = ["USD:damascus", "EUR:damascus", "TRY:damascus"]
    for key in keys:
        if key not in cached:
            return True
        if current[key]["buy"] != cached[key]["buy"] or current[key]["sell"] != cached[key]["sell"]:
            return True
    return False

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text
    }
    requests.post(url, json=payload)

def main():
    while True:
        try:
            rates = get_rates()
            cached = load_cache()

            if prices_changed(rates, cached):
                usd = rates["USD:damascus"]
                eur = rates["EUR:damascus"]
                try_lira = rates["TRY:damascus"]

                usd_old = cached.get("USD:damascus")
                eur_old = cached.get("EUR:damascus")
                try_old = cached.get("TRY:damascus")

                date = datetime.now(TZ).strftime("%d/%m/%Y %H:%M")

                message = (
                    f"💱 {date} أسعار الصرف في دمشق\n"
                    "━━━━━━━━━━━━━━━\n"
                    f"الدولار {get_emoji(usd_old['sell'] if usd_old else None, usd['sell'])}\n"
                    f"   شراء: {usd['buy']} | مبيع: {usd['sell']}\n\n"
                    f"اليورو {get_emoji(eur_old['sell'] if eur_old else None, eur['sell'])}\n"
                    f"   شراء: {eur['buy']} | مبيع: {eur['sell']}\n\n"
                    f"الليرة التركية {get_emoji(try_old['sell'] if try_old else None, try_lira['sell'])}\n"
                    f"   شراء: {try_lira['buy']} | مبيع: {try_lira['sell']}\n"
                    "━━━━━━━━━━━━━━━"
                )

                send_message(message)
                save_cache(rates)
                print(f"تم الإرسال {date}")
            else:
                print("لا تغيير")

        except Exception as e:
            print(f"خطأ: {e}")

        gc.collect()
        time.sleep(60)

if __name__ == "__main__":
    main()
