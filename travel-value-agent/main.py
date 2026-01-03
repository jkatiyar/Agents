import streamlit as st
import json
import os

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="Travel Value Agent",
    page_icon="🌄",
    layout="wide"
)

st.title("🌄 Travel Value Agent")
st.subheader("Step 8B: Family-Profile Aware Comparison")

# -------------------------------
# Traveller Profile (Fixed for now)
# -------------------------------
PROFILE = {
    "adults": 2,
    "kids": 1,
    "preferred_nights_min": 4,
    "preferred_nights_max": 6,
    "budget_per_adult": 40000,
    "avoid": ["Helicopter"]
}

st.markdown("""
### Traveller Profile
- 👨‍👩‍👧 2 Adults + 1 Kid  
- 🛏️ 4–6 Nights  
- 🌿 Relaxing, kid-friendly  
- 💰 Value for money (₹40k / adult max)
""")

# -------------------------------
# Load Plans
# -------------------------------
DATA_FILE = "data/valid_plans.json"

def load_plans():
    if not os.path.exists(DATA_FILE):
        st.error("valid_plans.json not found. Run parser.py first.")
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# -------------------------------
# Suitability Logic
# -------------------------------
def evaluate(plan):
    reasons = []
    score = 0

    nights = int(plan["Nights"])
    price = int(plan["Price Discounted"])

    # Nights
    if PROFILE["preferred_nights_min"] <= nights <= PROFILE["preferred_nights_max"]:
        score += 30
    else:
        reasons.append("❌ Nights not ideal for family")

    # Price
    if price <= PROFILE["budget_per_adult"]:
        score += 30
    else:
        reasons.append("❌ Too expensive per adult")

    # Helicopter check
    if "Helicopter" in plan["Package Name"]:
        reasons.append("❌ Helicopter-based (not kid/value friendly)")
    else:
        score += 20

    # Tour type
    if plan["Tour Type"] == "Customized Holidays":
        score += 20
    else:
        reasons.append("❌ Group tour (less flexible with kids)")

    if score >= 60:
        verdict = "🟢 Suitable"
    elif score >= 30:
        verdict = "🟡 Borderline"
    else:
        verdict = "🔴 Not Suitable"

    return verdict, reasons

# -------------------------------
# UI
# -------------------------------
if st.button("Evaluate Plans for My Family"):
    plans = load_plans()

    if not plans:
        st.warning("No plans available.")
    else:
        rows = []

        for p in plans:
            verdict, reasons = evaluate(p)

            rows.append({
                "Package Name": p["Package Name"],
                "Nights": p["Nights"],
                "Days": p["Days"],
                "Price (₹ / Adult)": p["Price Discounted"],
                "Tour Type": p["Tour Type"],
                "Verdict": verdict,
                "Why / Why Not": " | ".join(reasons) if reasons else "Good fit"
            })

        st.dataframe(rows, use_container_width=True)

        st.info(
            "ℹ️ Current plans are technically valid but mostly premium/helicopter-based. "
            "For true value-for-money family trips, the scraper needs to capture "
            "customized road-trip packages (Nainital, Mussoorie, Rishikesh, etc.)."
        )
