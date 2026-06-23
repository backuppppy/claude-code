#!/usr/bin/env python3
"""Interactive setup — creates .env with token and chat ID."""

import os
import requests


def get_chat_id(token: str) -> str:
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("ok") and data["result"]:
            for update in data["result"]:
                chat = update.get("message", {}).get("chat", {})
                if chat:
                    return str(chat["id"])
        return ""
    except Exception:
        return ""


def main():
    print("=== הגדרת בוט FXP לטלגרם ===\n")

    token = input("הדבק את הטוקן של הבוט (מ-@BotFather): ").strip()
    if not token:
        print("טוקן ריק, יוצא.")
        return

    # Verify token
    try:
        resp = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        me = resp.json()
        if not me.get("ok"):
            print(f"❌ טוקן לא תקין: {me.get('description', 'שגיאה לא ידועה')}")
            return
        bot_name = me["result"].get("username", "")
        print(f"✅ בוט מחובר: @{bot_name}")
    except Exception as e:
        print(f"❌ שגיאה בחיבור לטלגרם: {e}")
        return

    print("\nשלח הודעה כלשהי לבוט בטלגרם עכשיו, ואז לחץ Enter...")
    input()

    chat_id = get_chat_id(token)
    if chat_id:
        print(f"✅ זוהה Chat ID אוטומטית: {chat_id}")
    else:
        chat_id = input("לא זוהה אוטומטית. הכנס את Chat ID ידנית: ").strip()

    if not chat_id:
        print("Chat ID ריק, יוצא.")
        return

    interval = input("כל כמה שניות לבדוק (ברירת מחדל: 60)? ").strip() or "60"

    env_path = os.path.join(os.path.dirname(__file__), ".env")
    with open(env_path, "w") as f:
        f.write(f"TELEGRAM_TOKEN={token}\n")
        f.write(f"TELEGRAM_CHAT_ID={chat_id}\n")
        f.write(f"CHECK_INTERVAL={interval}\n")

    print(f"\n✅ נשמר ב-.env")
    print("כדי להפעיל את הבוט: python3 bot.py")
    print("כדי להפעיל ברקע:   nohup python3 bot.py &")


if __name__ == "__main__":
    main()
