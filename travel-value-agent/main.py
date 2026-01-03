import streamlit as st
import json
import os

from engine.place_intelligence_agent import get_place_intelligence
from engine.road_distance_agent import get_road_distance

st.set_page_config(
    page_title="Travel Value Agent",
    page_icon="🌄",
    layout="wide"
)

st.title("🌄 Travel Value Agent")
st.caption("Family-Friendly Travel Value Explorer")

DATA_FILE = "data/valid_plans.json"


def load_plans():
    if not os.path.exists(DATA_FILE):
        st.error("valid_plans.json not found. Run customized_plan_extractor.py first.")
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    clean = []
    for p in data:
        if (
            isinstance(p, dict)
            and p.get("Package Name")
            and p.get("Nights")
            and p.get("Days")
            and p.get("Price Discounted")
        ):
            clean.append(p)
    return clean


def travel_fatigue_by_road(start_city, first_place):
    km = get_road_distance(start_city, first_place)
    if km is None:
        return "Unknown", None

    if km < 200:
        return "Low", km
    elif km <= 400:
        return "Medium", km
    else:
        return "High", km


def senior_friendliness(fatigue, nights):
    score = 5
    if fatigue == "High":
        score -= 2
    if nights <= 3:
        score -= 1
    return max(score, 1)


def kid_friendliness(plan):
    score = 5
    if int(plan["Nights"]) <= 3:
        score -= 1
    if len(plan.get("Destinations", [])) >= 4:
        score -= 2
    if plan.get("Tour Type") == "Group Tour":
        score -= 1
    return max(score, 1)


def family_score(plan):
    score = 50
    score += kid_friendliness(plan) * 5
    return score


st.subheader("👨‍👩‍👧 Traveller Details")
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    adults = st.number_input("Adults", min_value=1, value=2)
with c2:
    kids = st.number_input("Kids", min_value=0, value=1)
with c3:
    month = st.selectbox(
        "Month of Travel",
        ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    )
with c4:
    nights_label = st.selectbox(
        "Preferred Nights",
        ["2-3", "3-4", "4-6", "Any"]
    )
with c5:
    start_city = st.selectbox(
        "Starting City",
        ["Delhi", "Mumbai", "Kolkata", "Chennai", "Hyderabad"]
    )

st.subheader("💰 Budget Preference")
budget_label = st.selectbox(
    "Price per adult (₹)",
    ["Any", "Under 20,000", "Under 30,000", "Under 40,000"]
)

nights_range = {
    "2-3": (2, 3),
    "3-4": (3, 4),
    "4-6": (4, 6),
    "Any": (1, 30)
}[nights_label]

max_price = {
    "Under 20,000": 20000,
    "Under 30,000": 30000,
    "Under 40,000": 40000,
    "Any": None
}[budget_label]


def filter_plans(plans):
    out = []
    for p in plans:
        nights = int(p["Nights"])
        price = int(p["Price Discounted"])
        if not (nights_range[0] <= nights <= nights_range[1]):
            continue
        if max_price and price > max_price:
            continue
        out.append(p)
    return out


if st.button("🔍 Find Best Plans"):
    plans = load_plans()
    plans = filter_plans(plans)

    st.success(f"{len(plans)} plans found")

    for i, plan in enumerate(plans, 1):
        st.markdown(f"## {i}. {plan['Package Name']}")
        st.write(f"🛏 Nights: {plan['Nights']} | 📅 Days: {plan['Days']}")
        st.write(f"💰 Price: ₹{plan['Price Discounted']}")
        st.write(f"🚌 Tour Type: {plan.get('Tour Type', 'N/A')}")
        st.write(f"👶 Kid Score: {kid_friendliness(plan)}/5")

        first_place = plan["Destinations"][0].split("(")[0].strip()
        fatigue, km = travel_fatigue_by_road(start_city, first_place)

        st.write(f"🚗 Road Travel: {start_city} → {first_place}")
        st.write(f"🧠 Road Fatigue: {fatigue}" + (f" (~{km} km)" if km else ""))

        st.write(f"🧓 Senior Friendliness: {senior_friendliness(fatigue, int(plan['Nights']))}/5")
        st.write(f"🏆 Family Score: {family_score(plan)}")

        if plan.get("Facilities"):
            st.write("🎯 Facilities:", ", ".join(plan["Facilities"]))

        with st.expander("🌍 View Place Details"):
            for dest in plan.get("Destinations", []):
                place = dest.split("(")[0].strip()
                st.markdown(f"### 📍 {place}")

                info = get_place_intelligence(place, month)

                st.write("🌡 Temperature:", info["temperature"])
                st.write("⛰ Altitude:", info["altitude"])
                st.write("🗣 Language:", info["language"])
                st.write("🍲 Local Food:", info["food"])
                st.write("💸 Avg Cost:", info["avg_cost"])
                st.write("👥 Crowd Density:", info["crowd_density"])
                st.write("🌧 Monsoon Risk:", info["monsoon_risk"])

        st.divider()
