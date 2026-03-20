import requests, json, re, subprocess
from html import unescape

ANKI_URL = "http://localhost:8765"

def anki(action, **params):
    response = requests.post(ANKI_URL, json={"action": action, "version": 6, "params": params})
    return response.json().get("result")

def strip_html(html):
    html = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', html, flags=re.DOTALL)
    html = re.sub(r'<br\s*/?>', '\n', html)
    html = re.sub(r'</div>', '\n', html)
    html = re.sub(r'<[^>]+>', '', html)
    html = re.sub(r'\n+', '\n', html)
    return unescape(html).strip()

def render_html_terminal(html):
    # w3m, lynx, or elinks - whichever you have
    for browser in ["w3m", "lynx", "elinks"]:
        try:
            result = subprocess.run(
                [browser, "-T", "text/html", "-dump", "/dev/stdin"],
                input=html.encode(),
                capture_output=True
            )
            if result.returncode == 0:
                print(result.stdout.decode())
                return
        except FileNotFoundError:
            continue
    # Fallback to strip_html
    print(strip_html(html))

def get_cards_in_order(deck_name):
    card_ids = anki("findCards", query=f"deck:{deck_name} is:due")
    
    if not card_ids:
        return []

    # Fetch info for all cards at once
    cards = anki("cardsInfo", cards=card_ids)

    # Reviews sorted by due date, learning cards by timestamp
    cards.sort(key=lambda c: (c["queue"], c["due"]))
    return cards

def review_cards(deck_name):
    # Get due card IDs
    cards = get_cards_in_order(deck_name)
    if not cards:
        print("No cards due!")
        return

    for card in cards:        
        render_html_terminal(card["question"])
        input("\nPress Enter to reveal answer...")

        render_html_terminal(card["answer"])

        # Rate the card: 1=Again, 2=Hard, 3=Good, 4=Easy
        while True:
            rating = input("\nRate (1=Again, 3=Good, ENTER=Exit): ")
            if rating in ("1", "3"):
                print(f"You rated: {'Again' if rating == '1' else 'Good'}")
                #anki("answerCards", answers=[{"cardId": card_id, "ease": int(rating)}])
                break
            elif rating == "":
                return

if __name__ == "__main__":
    review_cards("SM")
