# customized_plan_extractor.py
# Robust parser for Thomas Cook Uttarakhand packages
# ARCHITECTURE SAFE — single parser, VIEW DETAILS driven
# No transport bias | No stale assumptions | No hardcoding

import json
import os
import re

INPUT_FILE = "scraped_output.json"
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "valid_plans.json")

# -------------------------
# Regex patterns
# -------------------------
NIGHTS_RE = re.compile(r"(\d+)\s+Nights")
DAYS_RE = re.compile(r"(\d+)\s+Days")
DEST_RE = re.compile(r".*\(\d+N\)")
PRICE_RE = re.compile(r"(?:Rs\.|₹)\s*([\d\s]+)")
DISCOUNT_RE = re.compile(r"\d+% OFF")

# -------------------------
# Title filtering (CRITICAL)
# -------------------------
BLACKLIST_PHRASES = [
    "We use cookies",
    "I understand",
    "Customer Support",
    "Login",
    "Holidays",
    "Forex",
    "Flights",
    "Hotels",
    "Cruise",
    "Rail",
    "Loyalty",
    "Packages",
    "Modify Search",
    "Refine Search",
    "Sort by",
    "Compare",
    "Earn",
    "Loyalty Points",
    "People also ask",
    "Looking forward",
    "Trending",
    "ABOUT",
    "FOLLOW",
    "Certified",
    "Members",
    "Awards",
    "Submit",
    "Build your own Trip",
    "Customize your perfect holiday",
    "Video Chat",
    "Get a Quote",
]

def is_valid_title(line: str) -> bool:
    """
    Strict title detector.
    A valid package title must:
    - Be long enough
    - NOT contain prices, discounts, or navigation
    - NOT be cookie/footer/FAQ text
    """
    if len(line) < 10:
        return False

    if any(b.lower() in line.lower() for b in BLACKLIST_PHRASES):
        return False

    if "Rs." in line or "₹" in line:
        return False

    if "OFF" in line:
        return False

    if line.isupper():
        return False

    return True


def clean_price(text: str) -> str:
    return re.sub(r"[^\d]", "", text)


def extract():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError("❌ scraped_output.json not found")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = json.load(f)

    plans = []
    current = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # -----------------------------
        # 1️⃣ Start new plan
        # -----------------------------
        if current is None and is_valid_title(line):
            current = {
                "Package Name": line,
                "Nights": None,
                "Days": None,
                "Destinations": [],
                "Tour Type": None,
                "Facilities": [],
                "Price Original": None,
                "Price Discounted": None,
                "Discount": None,
            }
            continue

        if current is None:
            continue

        # -----------------------------
        # 2️⃣ Nights / Days
        # -----------------------------
        m = NIGHTS_RE.search(line)
        if m:
            current["Nights"] = m.group(1)
            continue

        m = DAYS_RE.search(line)
        if m:
            current["Days"] = m.group(1)
            continue

        # -----------------------------
        # 3️⃣ Destinations
        # -----------------------------
        if DEST_RE.match(line):
            current["Destinations"].append(line)
            continue

        # -----------------------------
        # 4️⃣ Tour Type
        # -----------------------------
        if line in ("Group Tour", "Customized Holidays"):
            current["Tour Type"] = line
            continue

        # -----------------------------
        # 5️⃣ Facilities
        # -----------------------------
        if line in ("Flights", "Hotels", "Sightseeing", "Meals"):
            if line not in current["Facilities"]:
                current["Facilities"].append(line)
            continue

        # -----------------------------
        # 6️⃣ Prices
        # -----------------------------
        if "Rs." in line or "₹" in line:
            m = PRICE_RE.search(line)
            if m:
                price = clean_price(m.group(1))
                if current["Price Original"] is None:
                    current["Price Original"] = price
                else:
                    current["Price Discounted"] = price
            continue

        # -----------------------------
        # 7️⃣ Discount
        # -----------------------------
        if DISCOUNT_RE.search(line):
            current["Discount"] = line
            continue

        # -----------------------------
        # 8️⃣ END OF PLAN (ONLY TRUSTED SIGNAL)
        # -----------------------------
        if line == "VIEW DETAILS":
            if (
                current["Package Name"]
                and current["Nights"]
                and current["Days"]
                and current["Price Discounted"]
            ):
                plans.append(current)
            current = None

    # -----------------------------
    # 9️⃣ Persist
    # -----------------------------
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(plans, f, indent=2, ensure_ascii=False)

    print(f"✅ Extracted {len(plans)} valid travel plans")
    print(f"📁 Output written to {OUTPUT_FILE}")


if __name__ == "__main__":
    extract()
