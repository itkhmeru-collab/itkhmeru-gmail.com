import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"


def request_json(url, data=None):
    payload = None if data is None else urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"User-Agent": "PU-NIN-Telegram-Setup/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            detail = json.loads(body).get("description", body)
        except Exception:
            detail = body
        raise RuntimeError(f"Telegram API HTTP {e.code}: {detail}") from e
    except Exception as e:
        raise RuntimeError(f"មិនអាចភ្ជាប់ Telegram API បាន៖ {e}") from e


def update_env(values):
    lines = ENV_FILE.read_text(encoding="utf-8-sig").splitlines() if ENV_FILE.exists() else []
    keys = set()
    out = []
    for line in lines:
        if "=" in line and not line.lstrip().startswith("#"):
            key = line.split("=", 1)[0].strip()
            if key in values:
                out.append(f"{key}={values[key]}")
                keys.add(key)
                continue
        out.append(line)
    for key, value in values.items():
        if key not in keys:
            out.append(f"{key}={value}")
    ENV_FILE.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    print("=" * 58)
    print(" PU NIN SECURITY - Telegram Alert Setup")
    print("=" * 58)
    if not ENV_FILE.exists():
        print("រកមិនឃើញ .env ទេ។ សូមដំណើរការ START_LOCAL.bat ម្តងសិន។")
        input("ចុច Enter ដើម្បីបិទ...")
        return 1
    print("Token និង Chat ID នឹងបញ្ចូលនៅលើ PC នេះប៉ុណ្ណោះ។ កុំផ្ញើវាក្នុង Chat។\n")
    token = input("បញ្ចូល Telegram Bot Token ពី @BotFather: ").strip()
    chat_id = input("បញ្ចូល Telegram Chat ID: ").strip()
    if not token or not chat_id or "PASTE_" in token or "PASTE_" in chat_id:
        print("Token ឬ Chat ID មិនទាន់បានបញ្ចូលត្រឹមត្រូវទេ។")
        input("ចុច Enter ដើម្បីបិទ...")
        return 1
    try:
        me = request_json(f"https://api.telegram.org/bot{token}/getMe")
        if not me.get("ok"):
            raise RuntimeError(me.get("description", "Bot token មិនត្រឹមត្រូវ។"))
        bot = me.get("result", {})
        # Validate chat and send a test alert before saving credentials.
        sent = request_json(f"https://api.telegram.org/bot{token}/sendMessage", {
            "chat_id": chat_id,
            "text": "✅ PU NIN SECURITY Telegram Alert បានភ្ជាប់ជោគជ័យ!\nBot: @" + bot.get("username", "unknown") + "\nការជូនដំណឹងសម្រាប់ Admin នឹងមកទីនេះ។"
        })
        if not sent.get("ok"):
            raise RuntimeError(sent.get("description", "ផ្ញើសារសាកល្បងមិនបាន។"))
        update_env({"TELEGRAM_BOT_TOKEN": token, "TELEGRAM_CHAT_ID": chat_id})
        print("\nជោគជ័យ! បានរក្សាទុក Token និង Chat ID ក្នុង .env។")
        print("បានផ្ញើសារសាកល្បងទៅ Telegram រួចហើយ។")
        print("\nឥឡូវបិទ Web Admin ប្រសិនបើកំពុងដំណើរការ ហើយបើក START_LOCAL.bat ឡើងវិញ។")
        print("Token ត្រូវបានរក្សាទុកតែក្នុង .env លើ PC របស់អ្នក។ កុំចែករំលែកឯកសារនេះ។")
    except Exception as e:
        print("\nភ្ជាប់មិនបាន៖", e)
        print("ពិនិត្យ Token/Chat ID និងថាបានផ្ញើ /start ទៅ Bot ឬអត់។")
        print("មិនបានរក្សាទុកតម្លៃថ្មីទេ។")
        input("ចុច Enter ដើម្បីបិទ...")
        return 1
    input("\nចុច Enter ដើម្បីបិទ...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
