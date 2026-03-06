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
DATA_SOURCE = os.environ.get("DATA_SOURCE")
CACHE_FILE = "cache.json"
TZ = pytz.timezone("Asia/Damascus")
scraper = cloudscraper.create_scraper()
KEYS = ("USD:damascus", "EUR:damascus", "TRY:damascus")

def get_rates():
    return scraper.get(DATA_SOURCE).json()["data"]["currencies"]

def load_cache():
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_cache(rates):
    with open(CACHE_FILE, "w") as f:
        json.dump({k: rates[k] for k in KEYS}, f)

def get_emoji(old, new):
    if old is None: return "🆕"
    return "📈" if new > old else "📉" if new < old else "➡️"

def prices_changed(current, cached):
    for k in KEYS:
        if k not in cached: return True
        if current[k]["buy"] != cached[k]["buy"] or current[k]["sell"] != cached[k]["sell"]: return True
    return False

def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHANNEL_ID, "text": text},
        timeout=10
    )

def main():
    while True:
        try:
            rates = get_rates()
            cached = load_cache()
            if prices_changed(rates, cached):
                date = datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
                send_message(
                    f"💱 {date} أسعار الصرف في دمشق\n"
                    "━━━━━━━━━━━━━━━\n"
                    f"الدولار {get_emoji(cached.get('USD:damascus', {}).get('sell'), rates['USD:damascus']['sell'])}\n"
                    f"   شراء: {rates['USD:damascus']['buy']} | مبيع: {rates['USD:damascus']['sell']}\n\n"
                    f"اليورو {get_emoji(cached.get('EUR:damascus', {}).get('sell'), rates['EUR:damascus']['sell'])}\n"
                    f"   شراء: {rates['EUR:damascus']['buy']} | مبيع: {rates['EUR:damascus']['sell']}\n\n"
                    f"الليرة التركية {get_emoji(cached.get('TRY:damascus', {}).get('sell'), rates['TRY:damascus']['sell'])}\n"
                    f"   شراء: {rates['TRY:damascus']['buy']} | مبيع: {rates['TRY:damascus']['sell']}\n"
                    "━━━━━━━━━━━━━━━"
                )
                save_cache(rates)
                print(f"تم الإرسال {date}")
            else:
                print("لا تغيير")
        except Exception as e:
            print(f"خطأ: {e}")
        finally:
            rates = None
            cached = None
            gc.collect()
        time.sleep(60)

if __name__ == "__main__":
    main()
