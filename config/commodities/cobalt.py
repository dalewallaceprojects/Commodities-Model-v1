"""
config/commodities/cobalt.py
Everything specific to Cobalt as a commodity.
To add a new commodity, duplicate this file and adjust the data.
"""

COMMODITY = {
    "name": "Cobalt",
    "symbol": "⬡",
    "default_ticker": "GC=F",
    "ticker_help": (
        "Cobalt has no direct futures ticker on Yahoo Finance. "
        "Use a proxy like GC=F (Gold) or a cobalt-linked equity."
    ),
}

# ─────────────────────────────────────────────
# PRODUCING REGIONS
# ─────────────────────────────────────────────
PRODUCING_REGIONS = {
    "DRC (Democratic Republic of Congo)": {
        "share": "~74%",
        "keywords": ["DRC", "Congo", "Katanga", "Lualaba", "Kolwezi", "Likasi"],
    },
    "Indonesia": {
        "share": "~5%",
        "keywords": ["Indonesia", "Sulawesi", "Morowali", "HPAL"],
    },
    "Russia": {
        "share": "~4%",
        "keywords": ["Russia", "Norilsk", "Nornickel"],
    },
    "Australia": {
        "share": "~3%",
        "keywords": ["Australia", "Murrin Murrin", "Cobalt Blue"],
    },
    "Philippines": {
        "share": "~3%",
        "keywords": ["Philippines", "Mindanao", "Palawan"],
    },
    "Cuba": {
        "share": "~2%",
        "keywords": ["Cuba", "Moa"],
    },
    "Canada": {
        "share": "~2%",
        "keywords": ["Canada", "Voisey", "Sudbury", "Cobalt Ontario"],
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
            "cobalt mining weather flooding DRC",
            "Congo mining rainy season disruption",
            "Indonesia nickel cobalt weather typhoon",
            "climate change cobalt mining",
            "cobalt mine flooding Katanga",
        ],
        "keywords": [
            "flood", "rain", "storm", "typhoon", "cyclone", "drought",
            "weather", "climate", "monsoon", "landslide", "erosion",
            "el nino", "la nina", "wet season", "dry season", "disaster",
        ],
    },
    "⚔️ Conflict & Instability": {
        "icon": "⚔️",
        "color": "#FF3B30",
        "queries": [
            "DRC Congo conflict mining cobalt",
            "DRC militia cobalt mine attack",
            "Congo political instability mining",
            "Russia sanctions cobalt nickel",
            "cobalt artisanal mining conflict",
        ],
        "keywords": [
            "conflict", "war", "militia", "rebel", "attack", "coup",
            "instability", "violence", "protest", "unrest", "military",
            "sanctions", "embargo", "tensions", "security", "armed",
            "M23", "rebel", "insurgent", "martial law", "political crisis",
        ],
    },
    "📜 Trade Policy & Sanctions": {
        "icon": "📜",
        "color": "#FFD700",
        "queries": [
            "cobalt export ban DRC policy",
            "cobalt tariff trade restriction",
            "DRC mining code royalty cobalt",
            "Indonesia export ban nickel cobalt",
            "cobalt critical mineral trade policy",
            "US EU cobalt supply chain regulation",
        ],
        "keywords": [
            "tariff", "ban", "export", "import", "sanction", "quota",
            "royalt", "tax", "levy", "duty", "trade war", "restriction",
            "regulation", "legislation", "policy", "law", "decree",
            "mining code", "beneficiation", "local processing",
        ],
    },
    "🌍 Environmental Regulation": {
        "icon": "🌍",
        "color": "#00FF88",
        "queries": [
            "cobalt mining environmental regulation",
            "DRC cobalt environmental impact",
            "cobalt ESG compliance mining",
            "cobalt child labour regulation",
            "responsible cobalt initiative",
            "cobalt mining pollution water contamination",
        ],
        "keywords": [
            "environment", "pollution", "contamination", "toxic",
            "ESG", "sustainability", "child labour", "child labor",
            "human rights", "due diligence", "responsible sourcing",
            "regulation", "compliance", "emission", "waste", "tailings",
            "deforestation", "biodiversity", "water quality",
        ],
    },
    "🚢 Supply Chain & Logistics": {
        "icon": "🚢",
        "color": "#FF9500",
        "queries": [
            "cobalt supply chain disruption",
            "cobalt shipping logistics delay",
            "cobalt stockpile shortage surplus",
            "cobalt refinery China processing",
            "cobalt battery demand EV supply",
            "cobalt mine shutdown closure",
        ],
        "keywords": [
            "supply chain", "logistics", "shipping", "transport",
            "shortage", "surplus", "stockpile", "inventory", "deficit",
            "refinery", "processing", "smelter", "shutdown", "closure",
            "delay", "bottleneck", "port", "rail", "infrastructure",
            "demand", "EV", "battery", "capacity", "production cut",
        ],
    },
}

# ─────────────────────────────────────────────
# LINKED EQUITIES
# ─────────────────────────────────────────────
LINKED_STOCKS = {
    "GLNCY": {
        "name": "Glencore",
        "relationship": "positive",
        "exposure": "Direct producer — cobalt is a primary revenue stream",
    },
    "VALE": {
        "name": "Vale S.A.",
        "relationship": "positive",
        "exposure": "Cobalt byproduct from nickel mining",
    },
    "BHP": {
        "name": "BHP Group",
        "relationship": "positive",
        "exposure": "Cobalt byproduct from nickel mining",
    },
    "CMCLF": {
        "name": "CMOC Group",
        "relationship": "positive",
        "exposure": "Direct producer — major DRC cobalt-copper mine",
    },
    "SBSW": {
        "name": "Sibanye Stillwater",
        "relationship": "positive",
        "exposure": "Growing battery metals portfolio including cobalt",
    },
    "TSLA": {
        "name": "Tesla",
        "relationship": "negative",
        "exposure": "Cobalt is a key battery cathode input — rising prices squeeze margins",
    },
    "6752.T": {
        "name": "Panasonic",
        "relationship": "negative",
        "exposure": "Battery cell manufacturer — cobalt is a direct input cost",
    },
    "ALB": {
        "name": "Albemarle",
        "relationship": "mixed",
        "exposure": "Indirect — benefits from cobalt substitution trends",
    },
    "RIVN": {
        "name": "Rivian",
        "relationship": "negative",
        "exposure": "EV producer — cobalt in NMC battery packs raises BOM costs",
    },
    "NIO": {
        "name": "NIO Inc.",
        "relationship": "negative",
        "exposure": "EV producer — cobalt is a significant battery material cost",
    },
    "MP": {
        "name": "MP Materials",
        "relationship": "mixed",
        "exposure": "Indirect — correlated through critical minerals policy sentiment",
    },
}
