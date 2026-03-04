import cloudscraper
import time
from datetime import datetime
import os
TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

def get_rates():
    scraper = cloudscraper.create_scraper()
    response = scraper.get("https://sse.sp-today.com/snapshot")
    data = response.json()
    return data["data"]["currencies"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text
    }
    requests.post(url, json=payload)

def main():
    while True:
        rates = get_rates()
        usd = rates["USD:damascus"]
        eur = rates["EUR:damascus"]
        try_lira = rates["TRY:damascus"]
        date = datetime.now().strftime("%d/%m/%Y")
        message = (
            f" {date}      أسعار الصرف في دمشق\n"
            "━━━━━━━━━━━━━━━\n"
            f"الدولار\n"
            f"   شراء: {usd['buy']} | مبيع: {usd['sell']}\n\n"
            f"اليورو\n"
            f"   شراء: {eur['buy']} | مبيع: {eur['sell']}\n\n"
            f"الليرة التركية\n"
            f"   شراء: {try_lira['buy']} | مبيع: {try_lira['sell']}\n"
            "━━━━━━━━━━━━━━━"
        )

        send_message(message)
        print("تم الإرسال، انتظار 6 ساعات...")
        time.sleep(6 * 60 * 60)

if __name__ == "__main__":

    main()


