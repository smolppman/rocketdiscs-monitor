import time
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://rocketdiscs.com/newly-added-discs"
BASE_URL = "https://www.rocketdiscs.com"
CHECK_INTERVAL = 300  # 5 Minuten

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
if not DISCORD_WEBHOOK_URL:
    raise RuntimeError("DISCORD_WEBHOOK_URL fehlt")

def fetch_product_links():
    response = requests.get(URL, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    links = set()
    for a in soup.select("a[href]"):
        href = a["href"]
        if "/products/" in href:
            links.add(urljoin(BASE_URL, href))

    return links

def send_discord_message(new_links):
    message = "🆕 **Neue RocketDiscs Artikel:**\n"
    for link in new_links:
        message += f"{link}\n"

    requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": message},
        timeout=10
    )

def main():
    print("Starte Monitoring…")
    known_links = fetch_product_links()

    while True:
        time.sleep(CHECK_INTERVAL)
        current_links = fetch_product_links()
        new_links = current_links - known_links

        if new_links:
            send_discord_message(new_links)
            known_links.update(new_links)
            print(f"{len(new_links)} neue Artikel")
        else:
            print("Keine neuen Artikel")

if __name__ == "__main__":
    main()
