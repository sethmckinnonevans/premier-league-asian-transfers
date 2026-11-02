
import re
from pathlib import Path

import httpx
import pandas as pd
from bs4 import BeautifulSoup


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

URL = (
    "https://www.transfermarkt.co.uk/premier-league/"
    "transfers/wettbewerb/GB1/saison_id/2026"
)

SEASON = "2026/27"
LEAGUE = "Premier League"
WINDOW = "summer"

OUTPUT_FILE = Path("2026.csv")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-GB,en;q=0.9",
}

COLUMNS = [
    "season",
    "league",
    "club",
    "window",
    "movement",
    "player_name",
    "player_id",
    "age",
    "nationality",
    "position",
    "pos",
    "market_value",
    "dealing_club",
    "dealing_country",
    "fee",
    "is_loan",
]


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def cell_text(cells, index):
    """Safely extract text from a table cell."""
    if index >= len(cells):
        return ""
    return cells[index].get_text(" ", strip=True)


def get_player_details(row, cells):
    """Extract the player's name and Transfermarkt ID."""
    player_link = row.find(
        "a", href=re.compile(r"/profil/spieler/\d+")
    )

    if player_link:
        href = player_link.get("href", "")
        match = re.search(r"/spieler/(\d+)", href)

        # Prefer the full name link where available.
        links = [
            a for a in cells[0].find_all("a", href=True)
            if "/profil/spieler/" in a["href"]
        ] if cells else [player_link]

        name_link = max(
            links,
            key=lambda a: len(a.get_text(" ", strip=True))
        ) if links else player_link

        return (
            name_link.get_text(" ", strip=True),
            match.group(1) if match else "",
        )

    return cell_text(cells, 0), ""


def get_nationality(cells):
    """Read nationality from the flag in the Nat. cell."""
    if len(cells) <= 2:
        return ""

    for img in cells[2].find_all("img"):
        nationality = img.get("title") or img.get("alt")
        if nationality:
            return nationality.strip()

    return ""


def get_dealing_country(cells):
    """Read the previous club's country from its flag."""
    if len(cells) <= 7:
        return ""

    images = cells[7].find_all("img")

    # The club cell commonly contains a club crest and a country flag.
    for img in reversed(images):
        country = img.get("title") or img.get("alt", "")
        if country and country.strip():
            return country.strip()

    return ""


def parse_fee(text):
    """Keep the original Transfermarkt fee text."""
    return text.strip() if text.strip() else ""


def detect_loan(row):
    """Look for loan indicators in row text, links or image labels."""
    row_text = row.get_text(" ", strip=True).lower()

    if "loan" in row_text or "loan fee" in row_text:
        return True

    for element in row.find_all(["img", "span", "a"]):
        labels = " ".join([
            str(element.get("title", "")),
            str(element.get("alt", "")),
            str(element.get("class", "")),
        ]).lower()

        if "loan" in labels:
            return True

    return False


# --------------------------------------------------
# SCRAPE PAGE
# --------------------------------------------------

print("Requesting Transfermarkt page...")

response = httpx.get(URL, headers=HEADERS, timeout=30)
print("HTTP status:", response.status_code)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
tables = soup.find_all("table")

records = []
clubs_seen = set()

for table in tables:
    rows = table.find_all("tr")
    if not rows:
        continue

    header_cells = rows[0].find_all(["th", "td"])
    direction = (
        header_cells[0].get_text(" ", strip=True)
        if header_cells else ""
    )

    # Ignore outgoing tables.
    if direction != "In":
        continue

    heading = table.find_previous(["h1", "h2", "h3", "h4"])
    club = heading.get_text(" ", strip=True) if heading else ""

    if not club:
        print("Warning: incoming table without a club heading.")
        continue

    clubs_seen.add(club)

    for row in rows[1:]:
        cells = row.find_all("td")

        # Ignore empty or malformed rows.
        if len(cells) < 8:
            continue

        player_name, player_id = get_player_details(row, cells)

        if not player_name:
            continue

        age_text = cell_text(cells, 1)
        try:
            age = int(age_text)
        except ValueError:
            age = None

        position = cell_text(cells, 3)
        pos = cell_text(cells, 4)
        market_value = cell_text(cells, 5)

        # On the page, the club and fee occupy the final two cells.
        # The intervening blank cell is retained in the page layout.
        dealing_club = cell_text(cells, 7) if len(cells) > 7 else ""
        fee = parse_fee(cell_text(cells, 8)) if len(cells) > 8 else ""

        # Extract the country from the previous club's flag.
        dealing_country = get_dealing_country(cells)

        records.append({
            "season": SEASON,
            "league": LEAGUE,
            "club": club,
            "window": WINDOW,
            "movement": "in",
            "player_name": player_name,
            "player_id": player_id,
            "age": age,
            "nationality": get_nationality(cells),
            "position": position,
            "pos": pos,
            "market_value": market_value,
            "dealing_club": dealing_club,
            "dealing_country": dealing_country,
            "fee": fee,
            "is_loan": detect_loan(row),
        })


# --------------------------------------------------
# SAVE AND VALIDATE
# --------------------------------------------------

df = pd.DataFrame(records, columns=COLUMNS)

if df.empty:
    raise RuntimeError(
        "No transfers were extracted. Check the page structure."
    )

df = df.drop_duplicates(
    subset=["club", "player_id", "dealing_club"],
    keep="first",
)

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("\n" + "=" * 50)
print("SCRAPE COMPLETE")
print("=" * 50)
print("Clubs found:", len(clubs_seen))
print("Transfers saved:", len(df))
print("Output file:", OUTPUT_FILE.resolve())

print("\nTransfers per club:")
print(df.groupby("club").size().sort_index().to_string())

print("\nMissing values by column:")
print(df.isna().sum().to_string())

print("\nSample records:")
print(df.head(10).to_string(index=False))

print("\nNationality examples:")
print(df[["player_name", "nationality", "dealing_club",
          "dealing_country", "fee"]].head(10).to_string(index=False))
