# Travel Value Agent — Project State

## Version: 1.0 (Frozen)
Date: 2026-01-03

### Frozen Layers
- Scraper: scraper.py
- Structured Data Contract: data/valid_plans.json
- Decision Logic: main.py (Step 8B)
- UI: Streamlit

### Data Contract (DO NOT CHANGE)
valid_plans.json is a list of dicts with fixed keys:
Package Name, Nights, Days, Destinations, Tour Type,
Facilities, Price Original, Price Discounted, Discount

### Architecture Principle
- Scrape → Parse → Validate → Decide → Display
- Each layer has exactly ONE responsibility

### Change Policy
- Enhancements must be additive
- No replacements
- No silent behavior changes
- Scanner must be run before changes

### Current Limitation (Accepted)
- Scraper captures premium helicopter tours only
- System correctly flags them as not value-friendly

### Next Possible Enhancements
- Non-helicopter package scraper
- Editable traveller profile UI
- Recommendation engine
- Multi-source comparison
