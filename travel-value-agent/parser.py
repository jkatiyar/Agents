import json
import os
import re

INPUT_FILE = "scraped_output.json"
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "valid_plans.json")


def is_package_title(line: str) -> bool:
    """
    Heuristic to detect package titles.
    Real packages usually:
    - Do not start with numbers
    - Are not questions
    - Are not prices
    - Contain key travel words
    """
    blacklist = [
        "When", "What", "How", "Why",
        "People also ask",
        "Looking forward",
        "Trending",
        "Packages",
        "Tour Packages",
        "Flights",
        "Submit",
        "About",
        "FOLLOW",
        "Certified",
        "Members"
    ]

    if any(line.startswith(b) for b in blacklist):
        return False

    if re.search(r"Rs\.", line):
        return False

    if re.search(r"\d+% OFF", line):
        return False

    keywords = [
        "Uttarakhand",
        "Dham",
        "Mussoorie",
        "Nainital",
        "Rishikesh",
        "Haridwar",
        "Ganges",
        "Corbett",
        "Kausani",
        "Ranikhet"
    ]

    return any(k in line for k in keywords)


def parse():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError("scraped_output.json not found")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = json.load(f)

    plans = []
    current = None

    for line in lines:
        line = line.strip()

        # 1️⃣ Detect new package
        if is_package_title(line):
            if current:
                plans.append(current)

            current = {
                "Package Name": line,
                "Nights": None,
                "Days": None,
                "Destinations": [],
                "Tour Type": None,
                "Facilities": [],
                "Price Original": None,
                "Price Discounted": None,
                "Discount": None
            }
            continue

        if not current:
            continue

        # 2️⃣ Nights / Days
        if re.match(r"\d+\s+Nights", line):
            current["Nights"] = line.split()[0]

        if re.match(r"\d+\s+Days", line):
            current["Days"] = line.split()[0]

        # 3️⃣ Destinations
        if re.search(r"\(\d+N\)", line):
            current["Destinations"].append(line)

        # 4️⃣ Tour Type
        if line in ["Group Tour", "Customized Holidays"]:
            current["Tour Type"] = line

        # 5️⃣ Facilities
        if line in ["Flights", "Hotels", "Sightseeing", "Meals"]:
            if line not in current["Facilities"]:
                current["Facilities"].append(line)

        # 6️⃣ Prices
        if re.match(r"Rs\.\s*\d", line):
            amount = re.sub(r"[^\d]", "", line)
            if not current["Price Original"]:
                current["Price Original"] = amount
            else:
                current["Price Discounted"] = amount

        # 7️⃣ Discount
        if re.match(r"\d+% OFF", line):
            current["Discount"] = line

    if current:
        plans.append(current)

    # 8️⃣ Final validation (hard filter)
    valid = []
    for p in plans:
        if (
            p["Package Name"]
            and p["Nights"]
            and p["Days"]
            and p["Price Discounted"]
        ):
            valid.append(p)

    # 9️⃣ Persist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(valid, f, ensure_ascii=False, indent=2)

    print(f"✅ Parsed {len(valid)} valid travel plans")
    print(f"📁 Output written to {OUTPUT_FILE}")


if __name__ == "__main__":
    parse()
