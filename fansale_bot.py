import os
import time
import requests
from bs4 import BeautifulSoup

# === KONFIGURATION ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
URL = "https://www.fansale.de/tickets/all/radiohead/520"  # <- deine Fansale-URL
SEARCH_TERM = "Angebot ab"               # <- z. B. Künstlername
CHECK_INTERVAL = 300                                # Sekunden zwischen Checks (z. B. 5 min)
HEALTH_INTERVAL = 43200                             # 12 Stunden in Sekunden

# === FUNKTION: Nachricht an Telegram senden ===
def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("WARN: BOT_TOKEN oder CHAT_ID nicht gesetzt. Nachricht nicht gesendet.")
        return
    try:
        resp = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={"chat_id": CHAT_ID, "text": message},
            timeout=10
        )
        if resp.status_code == 200:
            print(f"[OK] Telegram Nachricht gesendet: {message}")
        else:
            print(f"[WARN] Telegram API Fehler: {resp.status_code}")
    except Exception as e:
        print("Fehler beim Senden an Telegram:", e)


# === FUNKTION: Fansale-Seite prüfen ===
def check_site():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0 Safari/537.36"
        )
    }

    for attempt in range(3):
        try:
            r = requests.get(URL, headers=headers, timeout=30)
            r.raise_for_status()
            text = BeautifulSoup(r.text, "html.parser").get_text()
            found = SEARCH_TERM.lower() in text.lower()
            print(f"[OK] Versuch {attempt+1}: Seite erfolgreich abgerufen.")
            return found

        except requests.exceptions.Timeout:
            print(f"[WARN] Timeout bei Versuch {attempt+1}")
        except requests.exceptions.RequestException as e:
            print(f"[WARN] Netzwerkfehler bei Versuch {attempt+1}: {e}")

        time.sleep(5)  # warte 5 Sekunden vor erneutem Versuch

    # Nach 3 Fehlversuchen Telegram-Warnung senden
    send_telegram_message("⚠️ Fansale nicht erreichbar (3x Timeout oder Fehler).")
    return False


# === MAIN LOOP ===
def main():
    print("🚀 Fansale Watcher gestartet.")
    send_telegram_message("🤖 Fansale-Watcher ist gestartet!")

    last_health_ping = time.time()

    while True:
        try:
            if check_site():
                send_telegram_message("🎫 Tickets gefunden! Schnell prüfen!")
            else:
                print("[INFO] Keine Tickets gefunden.")

            # Alle 12 h Health-Ping schicken
            if time.time() - last_health_ping >= HEALTH_INTERVAL:
                send_telegram_message("✅ Bot läuft noch stabil.")
                last_health_ping = time.time()

        except Exception as e:
            print(f"[ERROR] Unerwarteter Fehler: {e}")
            send_telegram_message(f"⚠️ Unerwarteter Fehler: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
