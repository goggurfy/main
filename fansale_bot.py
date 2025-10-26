import requests
from bs4 import BeautifulSoup
import time

# ===== KONFIGURATION =====
URL = "https://www.fansale.de/tickets/all/radiohead/520"  # <- hier deine Event-Seite einfügen
CHECK_INTERVAL = 5  # Sekunden zwischen Checks
BOT_TOKEN = "8298211963:AAEXzbeLCMeiagQuB8JZ0CUqkzKcCzQiA78"
CHAT_ID = "30052226"
SEARCH_TERM = "Angebote ab"  # Text, auf den geachtet werden soll

# ===== FUNKTIONEN =====
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def check_site():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.get_text()
    return SEARCH_TERM.lower() in content.lower()

# ===== HAUPTSCHLEIFE =====
def main():
    last_status = None
    print(f"👀 Beobachte {URL}")
    while True:
        try:
            available = check_site()
            if available != last_status:
                status_text = "✅ Tickets verfügbar!" if available else "❌ Keine Tickets mehr."
                send_message(f"{status_text}\n{URL}")
                last_status = available
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"Fehler: {e}")
            time.sleep(120)

if __name__ == "__main__":
    main()