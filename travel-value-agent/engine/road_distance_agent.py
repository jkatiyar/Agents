# engine/road_distance_agent.py
# Deterministic road-distance estimator (NO APIs, NO internet)

CITY_DISTANCES_KM = {
    # Delhi
    ("Delhi", "Haridwar"): 220,
    ("Delhi", "Rishikesh"): 240,
    ("Delhi", "Mussoorie"): 290,
    ("Delhi", "Nainital"): 320,
    ("Delhi", "Corbett"): 260,
    ("Delhi", "Kausani"): 410,
    ("Delhi", "Ranikhet"): 360,

    # Mumbai
    ("Mumbai", "Haridwar"): 1650,
    ("Mumbai", "Rishikesh"): 1680,
    ("Mumbai", "Mussoorie"): 1720,

    # Kolkata
    ("Kolkata", "Haridwar"): 1500,
    ("Kolkata", "Rishikesh"): 1520,

    # Chennai
    ("Chennai", "Haridwar"): 2300,

    # Hyderabad
    ("Hyderabad", "Haridwar"): 1650,
}


def get_road_distance(start_city: str, destination: str):
    """
    Returns distance in km (int) or None if unknown.
    """
    key = (start_city, destination)
    return CITY_DISTANCES_KM.get(key)
