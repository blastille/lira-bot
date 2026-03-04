import requests
import time
from datetime import datetime
TOKEN = ""
CHANNEL_ID = "@ite_archive"

def get_rates():
    url = "https://sse.sp-today.com/snapshot"
    response = requests.get(url)
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
            f"💱 {date} أسعار الصرف في دمشق\n"
            "━━━━━━━━━━━━━━━\n"
            f"الدولار\n"
            f"   شراء: {usd['buy']} | بيع: {usd['sell']}\n\n"
            f"اليورو\n"
            f"   شراء: {eur['buy']} | بيع: {eur['sell']}\n\n"
            f"الليرة التركية\n"
            f"   شراء: {try_lira['buy']} | بيع: {try_lira['sell']}\n"
            "━━━━━━━━━━━━━━━"
        )

        send_message(message)
        print("تم الإرسال، انتظار 6 ساعات...")
        time.sleep(6 * 60 * 60)

if __name__ == "__main__":
    main()