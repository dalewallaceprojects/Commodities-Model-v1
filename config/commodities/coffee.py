"""
config/commodities/coffee.py
Everything specific to Coffee as a commodity.
To add a new commodity, duplicate this file and adjust the data.
"""

from config.commodities.coffee_geo import MINES, REFINERIES, PORTS, CHOKEPOINTS, ROUTES

GEO_DATA = {
    "mines": MINES,
    "refineries": REFINERIES,
    "ports": PORTS,
    "chokepoints": CHOKEPOINTS,
    "ROUTES": ROUTES,
    "mine_label": "Plantations",
}

COMMODITY = {
    "name": "Coffee",
    "symbol": "☕",
    "default_ticker": "KC=F",
    "ticker_help": (
        "KC=F is the ICE Coffee C Arabica futures contract on Yahoo Finance. "
        "Alternatives: JO (iPath Coffee ETN)."
    ),
}

# ─────────────────────────────────────────────
# PRODUCING REGIONS
# ─────────────────────────────────────────────
PRODUCING_REGIONS = {
    "Brazil": {
        "share": "~35%",
        "keywords": ["Brazil", "Minas Gerais", "São Paulo", "Paraná", "Espírito Santo", "Bahia"],
    },
    "Vietnam": {
        "share": "~18%",
        "keywords": ["Vietnam", "Dak Lak", "Lam Dong", "Gia Lai", "Central Highlands", "Buon Ma Thuot"],
    },
    "Colombia": {
        "share": "~7%",
        "keywords": ["Colombia", "Antioquia", "Caldas", "Tolima", "Huila", "Nariño"],
    },
    "Indonesia": {
        "share": "~7%",
        "keywords": ["Indonesia", "Sumatra", "Java", "Sulawesi", "Flores", "Toraja"],
    },
    "Ethiopia": {
        "share": "~5%",
        "keywords": ["Ethiopia", "Sidamo", "Yirgacheffe", "Guji", "Jimma", "Harrar"],
    },
    "Honduras": {
        "share": "~4%",
        "keywords": ["Honduras", "Copán", "Ocotepeque", "Lempira", "Santa Barbara"],
    },
    "Uganda": {
        "share": "~3%",
        "keywords": ["Uganda", "Mount Elgon", "Rwenzori", "Bugisu"],
    },
    "Peru": {
        "share": "~3%",
        "keywords": ["Peru", "Cajamarca", "Junín", "San Martín", "Cusco"],
    },
}

# ─────────────────────────────────────────────
# RISK CATEGORIES & SEARCH QUERIES
# ─────────────────────────────────────────────
RISK_CATEGORIES = {
    "🌪️ Weather & Climate": {
        "icon": "🌪️",
        "color": "#00BFFF",
        "queries": [
            "coffee crop weather drought Brazil",
            "Brazil frost coffee harvest damage",
            "Vietnam coffee drought Central Highlands",
            "Colombia coffee rain flooding harvest",
            "El Nino La Nina coffee production impact",
            "climate change coffee growing regions",
            "Ethiopia coffee drought crop failure",
        ],
        "keywords": [
            "flood", "rain", "storm", "typhoon", "cyclone", "drought",
            "weather", "climate", "frost", "freeze", "hail", "heatwave",
            "monsoon", "landslide", "erosion", "el nino", "la nina",
            "wet season", "dry season", "disaster", "crop damage",
            "blossom", "flowering", "irrigation",
        ],
    },
    "⚔️ Conflict & Instability": {
        "icon": "⚔️",
        "color": "#FF3B30",
        "queries": [
            "Colombia coffee conflict FARC farmers",
            "Ethiopia coffee political instability Tigray",
            "Honduras coffee violence migration farmers",
            "coffee farmer protests Latin America",
            "Uganda coffee political unrest",
        ],
        "keywords": [
            "conflict", "war", "militia", "rebel", "attack", "coup",
            "instability", "violence", "protest", "unrest", "military",
            "sanctions", "embargo", "tensions", "security", "armed",
            "FARC", "guerrilla", "insurgent", "political crisis",
            "migration", "displacement", "cartel",
        ],
    },
    "📜 Trade Policy & Sanctions": {
        "icon": "📜",
        "color": "#FFD700",
        "queries": [
            "coffee tariff trade war import duty",
            "EU deforestation regulation coffee imports",
            "Brazil coffee export tax policy",
            "US coffee tariff 2025 2026",
            "coffee trade restriction quota ICO",
            "Vietnam coffee export regulation",
        ],
        "keywords": [
            "tariff", "ban", "export", "import", "sanction", "quota",
            "royalt", "tax", "levy", "duty", "trade war", "restriction",
            "regulation", "legislation", "policy", "law", "decree",
            "deforestation regulation", "EUDR", "traceability",
            "customs", "trade agreement", "WTO",
        ],
    },
    "🌍 Environmental Regulation": {
        "icon": "🌍",
        "color": "#00FF88",
        "queries": [
            "coffee deforestation sustainability regulation",
            "EU deforestation free coffee supply chain",
            "coffee farming environmental impact water",
            "fair trade coffee certification 2025 2026",
            "coffee child labour regulation",
            "organic coffee certification growth",
            "coffee pesticide regulation ban",
        ],
        "keywords": [
            "environment", "pollution", "contamination", "deforestation",
            "ESG", "sustainability", "child labour", "child labor",
            "human rights", "due diligence", "responsible sourcing",
            "regulation", "compliance", "organic", "fair trade",
            "rainforest alliance", "UTZ", "certification", "biodiversity",
            "shade grown", "agroforestry", "water usage", "pesticide",
        ],
    },
    "🚢 Supply Chain & Logistics": {
        "icon": "🚢",
        "color": "#FF9500",
        "queries": [
            "coffee supply chain disruption shipping",
            "coffee shortage global supply deficit",
            "coffee warehouse stockpile ICE inventory",
            "coffee shipping container freight cost",
            "coffee port congestion export delay",
            "coffee roaster supply shortage price",
            "coffee bean processing plant capacity",
        ],
        "keywords": [
            "supply chain", "logistics", "shipping", "transport",
            "shortage", "surplus", "stockpile", "inventory", "deficit",
            "warehouse", "processing", "roaster", "shutdown", "closure",
            "delay", "bottleneck", "port", "freight", "container",
            "demand", "consumption", "capacity", "production cut",
            "ICE certified stocks", "exchange stocks",
        ],
    },
    "🦠 Crop Disease & Pests": {
        "icon": "🦠",
        "color": "#E040FB",
        "queries": [
            "coffee leaf rust outbreak roya",
            "coffee berry borer pest damage",
            "coffee disease fungus crop loss",
            "coffee pest infestation Latin America Africa",
            "coffee wilt disease Uganda",
        ],
        "keywords": [
            "rust", "roya", "leaf rust", "borer", "berry borer",
            "pest", "disease", "fungus", "blight", "wilt",
            "infestation", "outbreak", "crop loss", "resistant variety",
            "nematode", "antestia", "CBD", "coffee berry disease",
        ],
    },
}

# ─────────────────────────────────────────────
# LINKED EQUITIES
# ─────────────────────────────────────────────
LINKED_STOCKS = {
    # ── Positive: higher coffee prices benefit these ──
    "FARM": {
        "name": "Farmer Bros.",
        "relationship": "positive",
        "exposure": "Coffee roaster & wholesaler — benefits from higher-margin pricing environment",
    },
    "JVA": {
        "name": "Coffee Holding Co.",
        "relationship": "positive",
        "exposure": "Small-cap coffee roaster & distributor — revenue tied to coffee volumes",
    },
    "BRCC": {
        "name": "BRC Inc. (Black Rifle Coffee)",
        "relationship": "positive",
        "exposure": "DTC premium coffee brand — brand pricing power offsets input costs",
    },
    # ── Negative: higher coffee prices hurt these ──
    "SBUX": {
        "name": "Starbucks",
        "relationship": "negative",
        "exposure": "World's largest coffee chain — higher bean costs squeeze cafe margins",
    },
    "BROS": {
        "name": "Dutch Bros",
        "relationship": "negative",
        "exposure": "Fast-growing drive-thru chain — bean cost inflation pressures unit economics",
    },
    "KDP": {
        "name": "Keurig Dr Pepper",
        "relationship": "negative",
        "exposure": "K-Cup & packaged coffee — raw bean prices directly impact COGS",
    },
    "SJM": {
        "name": "J.M. Smucker",
        "relationship": "negative",
        "exposure": "Owns Folgers, Café Bustelo, Dunkin' retail — coffee is ~32% of revenue",
    },
    "NSRGY": {
        "name": "Nestlé",
        "relationship": "negative",
        "exposure": "Nescafé, Nespresso, Starbucks at-home — world's largest coffee company by volume",
    },
    "QSR": {
        "name": "Restaurant Brands Intl.",
        "relationship": "negative",
        "exposure": "Owns Tim Hortons — coffee supply chain costs impact highest-margin segment",
    },
    # ── Mixed ──
    "LKNCY": {
        "name": "Luckin Coffee",
        "relationship": "mixed",
        "exposure": "China's largest coffee chain — rapid growth may offset input cost pressure",
    },
    "MCD": {
        "name": "McDonald's",
        "relationship": "mixed",
        "exposure": "McCafé is a growing segment — coffee is material but diversified menu absorbs cost",
    },
}

# ─────────────────────────────────────────────
# SUPPLY CHAIN GEOGRAPHY
# ─────────────────────────────────────────────
from config.commodities.coffee_geo import MINES, REFINERIES, PORTS, CHOKEPOINTS, ROUTES
GEO = {"mines": MINES, "refineries": REFINERIES, "ports": PORTS, "chokepoints": CHOKEPOINTS, "routes": ROUTES}
