import time
import json
import requests
from threading import Thread
from flask import Flask

# Flask web server na udržení běhu služby na Renderu
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Roblox status tracker běží."

def run_flask():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_flask).start()

# Roblox user IDs
MAIN_USER_ID = 2426183398
FRIEND_USER_ID = 2040065235

# Tvůj Discord webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1387843662376992768/F7OtWTZ1rGFs6Uwq-RETN0yGYHLmpMGj7vwgVhheNPAsXuRPO45AUs5JmhTMvnxFYy0l"

# Roblox Presence API
PRESENCE_API = "https://presence.roblox.com/v1/presence/users"

last_status = None

def get_presence(user_ids):
    try:
        response = requests.post(
            PRESENCE_API,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"userIds": user_ids})
        )
        response.raise_for_status()
        data = response.json()
        print(f"DEBUG: Presence data fetched: {data}")
        return {entry["userId"]: entry for entry in data.get("userPresences", [])}
    except Exception as e:
        print(f"❌ Chyba při načítání přítomnosti: {e}")
        return {}

def send_to_discord(message):
    try:
        res = requests.post(WEBHOOK_URL, json={"content": message})
        print(f"DEBUG: Discord webhook response: {res.status_code} {res.text}")
        if not res.ok:
            print(f"❌ Chyba při odesílání webhooku: {res.status_code} {res.text}")
    except Exception as e:
        print(f"❌ Výjimka při odesílání na Discord: {e}")

def main():
    global last_status
    while True:
        presence_data = get_presence([MAIN_USER_ID, FRIEND_USER_ID])
        main_data = presence_data.get(MAIN_USER_ID)
        friend_data = presence_data.get(FRIEND_USER_ID)

        if main_data and main_data.get("userPresenceType") == 2:
            if friend_data and friend_data.get("userPresenceType") == 2:
                if main_data.get("placeId") == friend_data.get("placeId"):
                    status = f"🟢 Online ve hře s kamarádkou - https://www.roblox.com/users/{MAIN_USER_ID}/profile"
                else:
                    status = f"🟢 Online ve hře - https://www.roblox.com/users/{MAIN_USER_ID}/profile"
            else:
                status = f"🟢 Online ve hře - https://www.roblox.com/users/{MAIN_USER_ID}/profile"
        elif main_data:
            status = f"🔴 Offline - https://www.roblox.com/users/{MAIN_USER_ID}/profile"
        else:
            status = "⚠️ Nelze zjistit stav"

        if status != last_status:
            send_to_discord(status)
            print(f"[{time.strftime('%H:%M:%S')}] Odesláno: {status}")
            last_status = status
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Stav nezměněn.")

        time.sleep(30)

if __name__ == "__main__":
    print("✅ Skript spuštěn, čekám na data...")
    main()
