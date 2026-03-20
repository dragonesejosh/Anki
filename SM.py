import re, subprocess, os
from html import unescape
from anki.collection import Collection

ANKI_DECK_LIN = "/mnt/c/Users/joshu/AppData/Roaming/Anki2/Joshua Gan/collection.anki2"
ANKI_DECK_WIN = "C:/Users/joshu/AppData/Roaming/Anki2/Joshua Gan/collection.anki2"

def strip_html(html):
    html = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', html, flags=re.DOTALL)
    html = re.sub(r'<br\s*/?>', '\n', html)
    html = re.sub(r'</div>', '\n', html)
    html = re.sub(r'<[^>]+>', '', html)
    html = re.sub(r'&nbsp;', ' ', html)
    html = re.sub(r'\n+', '\n', html)
    return unescape(html).strip()

def render_html_terminal(html):
    try:
        subprocess.run(['w3m', '-T', 'text/html', '-dump', '-cols', '64'],
                       input=html.encode(), check=True)
    except Exception:
        print(strip_html(html))

def get_cards_in_order(col, deck_name):
    card_ids = col.find_cards(f"deck:{deck_name} is:due")
    
    if not card_ids:
        return []

    # Fetch info for all cards at once
    cards = [col.get_card(cid) for cid in card_ids]

    # Reviews sorted by due date, learning cards by timestamp
    cards.sort(key=lambda c: (c.queue, c.due))
    return cards

c = None
def review_cards(deck_name):
    global c

    # Check if LIN exists
    if os.path.exists(ANKI_DECK_LIN):
        col = Collection(ANKI_DECK_LIN)
    elif os.path.exists(ANKI_DECK_WIN):
        col = Collection(ANKI_DECK_WIN)
    else:
        print("Anki deck not found!")
        return

    # Get due card IDs
    cards = get_cards_in_order(col, deck_name)
    if not cards:
        print("No cards due!")
        return

    try:
        for (i, card) in enumerate(cards):
            display = card.render_output()
            c = display
            print(f"> Card {i + 1}:\n")
            render_html_terminal(display.question_text)
            input("\n> Press Enter to reveal answer...")
            print()

            render_html_terminal(display.answer_text)

            # Rate the card: 1=Again, 2=Hard, 3=Good, 4=Easy
            while True:
                rating = input("\n> Rate (1=Again, 3=Good, ENTER=Exit): ")
                if rating in ("1", "3"):
                    print(f"> You rated: {'Again' if rating == '1' else 'Good'}\n")
                    col.sched.answerCard(card, int(rating))
                    break
                elif rating == "":
                    return
    except Exception:
        pass
    finally:
        col.close()

def main():
    review_cards("SM")

if __name__ == "__main__":
    main()
