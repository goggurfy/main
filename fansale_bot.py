# fansale_watcher.py
import os
import time
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask

# ===== KONFIGURATION (aus ENV) =====
URL = os.getenv("EVENT_URL", "https://www.fansale.de/tickets/all/radiohead/520")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))  # Sekunden
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SEARCH_TERM = os.getenv("SEARCH_TERM", "Angebote ab")

# ===== Telegram senden =====
def send_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("WARN: BOT_TOKEN oder CHAT_ID nicht gesetzt. Nachricht nicht gesendet.")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
        print("Telegram Response:", resp.status_code, resp.text)
    except Exception as e:
        print("Fehler beim Telegram senden:", e)

# ===== Seite prüfen =====
def check_site():
    try:
        r = requests.get(URL, timeout=15)
        r.raise_for_status()
        text = BeautifulSoup(r.text, "html.parser").get_text()
        return SEARCH_TERM.lower() in text.lower()
    except Exception as e:
        print("Fehler beim Abrufen/Auswerten:", e)
        return False

# ===== Monitoring-Loop =====
def watcher_loop():
    last = None
    # Beim ersten Start kurz testen, ob Telegram läuft
    try:
        send_message("🚀 Fansale-Watcher gestartet (Testnachricht).")
    except Exception as e:
        print("Test-Nachricht fehlgeschlagen:", e)

    print("Starte Monitoring für:", URL)
    while True:
        available = check_site()
        if available != last:
            msg = ("✅ Tickets verfügbar!\n" if available else "❌ Keine Tickets mehr.\n") + URL
            send_message(msg)
            last = available
        time.sleep(CHECK_INTERVAL)

# ===== Flask-App (einfacher Health-Endpoint) =====
app = Flask(__name__)

@app.route("/")
def index():
    return "Fansale-Watcher läuft."

@app.route("/health")
def health():
    return "ok"

# Start watcher in Background-Thread beim Import (Gunicorn importiert das Modul)
threading.Thread(target=watcher_loop, daemon=True).start()

# gunicorn sucht nach 'app' im Modul, daher exportieren wir 'app' oben
