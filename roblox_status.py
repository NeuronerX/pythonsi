import time
import json
import requests

# Roblox user IDs
MAIN_USER_ID = 2426183398
FRIEND_USER_ID = 2040065235

# Discord Webhook URL
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
        return {entry["userId"]: entry for entry in data["userPresences"]}
    except Exception as e:
        print(f"Chyba při načítání přítomnosti: {e}")
        return {}

def send_to_discord(message):
    try:
        requests.post(WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Chyba při odesílání na Discord: {e}")

def main():
    global last_status
    while True:
        presence_data = get_presence([MAIN_USER_ID, FRIEND_USER_ID])
        main_data = presence_data.get(MAIN_USER_ID)
        friend_data = presence_data.get(FRIEND_USER_ID)

        if main_data and main_data["userPresenceType"] == 2:
            # Hlavní uživatel je ve hře
            if friend_data and friend_data["userPresenceType"] == 2:
                # Kamarádka je taky ve hře
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
    main()
