import os
import json

CACHE_DIR = "data/place_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# -------------------------------------------------
# STATIC ROAD MATRIX (PHASE 1)
# -------------------------------------------------
ROAD_MATRIX = {
    "Delhi": {
        "Dehradun": (245, 6),
        "Haridwar": (220, 5.5),
        "Rishikesh": (240, 6),
        "Mussoorie": (290, 8),
        "Nainital": (300, 8.5),
        "Corbett": (260, 7),
        "Kausani": (420, 12),
        "Ranikhet": (380, 11),
    }
}

# -------------------------------------------------
# STATIC PLACE INTELLIGENCE
# -------------------------------------------------
PLACE_PROFILES = {
    "Dehradun": {
        "language": "Hindi, Garhwali, Kumaoni",
        "food": "Kafuli, Aloo ke Gutke, Chainsoo",
        "avg_cost": "₹1,000–₹2,000 / day",
        "crowd_density": "Low",
        "senior_friendliness": 4,
    },
    "Haridwar": {
        "language": "Hindi",
        "food": "Kachori, Aloo Puri",
        "avg_cost": "₹800–₹1,500 / day",
        "crowd_density": "High",
        "senior_friendliness": 4,
    },
    "Rishikesh": {
        "language": "Hindi",
        "food": "Satvik Thali",
        "avg_cost": "₹1,000–₹2,000 / day",
        "crowd_density": "High",
        "senior_friendliness": 3,
    },
    "Mussoorie": {
        "language": "Hindi",
        "food": "Maggi, Tibetan food",
        "avg_cost": "₹1,500–₹2,500 / day",
        "crowd_density": "Medium",
        "senior_friendliness": 3,
    },
    "Nainital": {
        "language": "Hindi, Kumaoni",
        "food": "Momoz, Street snacks",
        "avg_cost": "₹1,500–₹2,500 / day",
        "crowd_density": "Medium",
        "senior_friendliness": 3,
    }
}

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def _default_payload():
    return {
        "temperature": "Not available",
        "altitude": "Not available",
        "language": "Not available",
        "food": "Not available",
        "avg_cost": "Not available",
        "crowd_density": "Unknown",
        "senior_friendliness": "Unknown",
        "monsoon_risk": "Unknown",
        "road_distance_km": "Unknown",
        "road_time_hr": "Unknown",
        "road_fatigue": "Unknown",
    }


def _infer_temperature(month):
    if month in ["Dec", "Jan", "Feb"]:
        return "5–15°C"
    if month in ["Apr", "May", "Jun"]:
        return "20–35°C"
    return "10–25°C"


def _monsoon_risk(month):
    if month in ["Jul", "Aug"]:
        return "High"
    if month in ["Jun", "Sep"]:
        return "Medium"
    return "Low"


def _road_fatigue(hours):
    if hours == "Unknown":
        return "Unknown"
    if hours <= 5:
        return "Low"
    if hours <= 8:
        return "Medium"
    return "High"


# -------------------------------------------------
# MAIN ENTRY (SAFE, COMPLETE)
# -------------------------------------------------
def get_place_intelligence(place: str, month: str, start_city: str = "Delhi"):
    data = _default_payload()

    # Static enrichment
    profile = PLACE_PROFILES.get(place)
    if profile:
        data.update(profile)

    # Temperature & monsoon
    data["temperature"] = _infer_temperature(month)
    data["monsoon_risk"] = _monsoon_risk(month)

    # Road info
    road = ROAD_MATRIX.get(start_city, {}).get(place)
    if road:
        km, hrs = road
        data["road_distance_km"] = km
        data["road_time_hr"] = hrs
        data["road_fatigue"] = _road_fatigue(hrs)

    return data
