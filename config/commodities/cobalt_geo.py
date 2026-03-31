"""
config/commodities/cobalt_geo.py
Geographic data for cobalt supply chain mapping.
"""

MINES = [
    {"name": "Mutanda Mine", "lat": -10.78, "lng": 25.95, "country": "DRC", "operator": "Glencore"},
    {"name": "Tenke Fungurume", "lat": -10.60, "lng": 26.10, "country": "DRC", "operator": "CMOC"},
    {"name": "Kamoto Mine", "lat": -10.73, "lng": 25.43, "country": "DRC", "operator": "Glencore/Katanga"},
    {"name": "Kisanfu Mine", "lat": -10.95, "lng": 26.25, "country": "DRC", "operator": "CMOC"},
    {"name": "Voiseys Bay", "lat": 56.33, "lng": -62.08, "country": "Canada", "operator": "Vale"},
    {"name": "Murrin Murrin", "lat": -28.72, "lng": 121.87, "country": "Australia", "operator": "Minara/Glencore"},
    {"name": "Norilsk", "lat": 69.35, "lng": 88.20, "country": "Russia", "operator": "Nornickel"},
    {"name": "Morowali HPAL", "lat": -2.85, "lng": 121.90, "country": "Indonesia", "operator": "Various (Chinese JV)"},
    {"name": "Moa Nickel", "lat": 20.65, "lng": -75.95, "country": "Cuba", "operator": "Sherritt Intl."},
    {"name": "Taganito HPAL", "lat": 9.22, "lng": 125.82, "country": "Philippines", "operator": "NAAC/Sumitomo"},
]

REFINERIES = [
    {"name": "Huayou Cobalt (Quzhou)", "lat": 28.97, "lng": 118.87, "country": "China"},
    {"name": "GEM Co. (Jingmen)", "lat": 31.03, "lng": 112.20, "country": "China"},
    {"name": "CNGR Advanced Material", "lat": 28.22, "lng": 112.94, "country": "China"},
    {"name": "Umicore (Kokkola)", "lat": 63.84, "lng": 23.13, "country": "Finland"},
    {"name": "Freeport Cobalt (Kokkola)", "lat": 63.84, "lng": 23.14, "country": "Finland"},
    {"name": "Vale Long Harbour", "lat": 47.42, "lng": -53.83, "country": "Canada"},
    {"name": "Sumitomo (Niihama)", "lat": 33.96, "lng": 133.32, "country": "Japan"},
    {"name": "Chambishi (CNMC)", "lat": -12.63, "lng": 28.05, "country": "Zambia"},
]

PORTS = [
    {"name": "Durban", "lat": -29.87, "lng": 31.03, "country": "South Africa", "role": "DRC cobalt export hub"},
    {"name": "Dar es Salaam", "lat": -6.82, "lng": 39.28, "country": "Tanzania", "role": "East African export route"},
    {"name": "Walvis Bay", "lat": -22.95, "lng": 14.51, "country": "Namibia", "role": "Lobito corridor Atlantic terminal"},
    {"name": "Shanghai", "lat": 31.23, "lng": 121.47, "country": "China", "role": "Major cobalt import hub"},
    {"name": "Ningbo-Zhoushan", "lat": 29.87, "lng": 121.55, "country": "China", "role": "Chinese import terminal"},
    {"name": "Rotterdam", "lat": 51.92, "lng": 4.48, "country": "Netherlands", "role": "European trading hub"},
    {"name": "Antwerp", "lat": 51.26, "lng": 4.40, "country": "Belgium", "role": "Historic cobalt trading centre"},
]

CHOKEPOINTS = [
    {"name": "Suez Canal", "lat": 30.46, "lng": 32.35},
    {"name": "Strait of Malacca", "lat": 2.50, "lng": 101.20},
    {"name": "Cape of Good Hope", "lat": -34.36, "lng": 18.47},
    {"name": "Bab el-Mandeb", "lat": 12.58, "lng": 43.33},
    {"name": "Lobito Corridor", "lat": -12.33, "lng": 13.55},
]

ROUTES = [
    {
        "name": "DRC → China (via Cape)",
        "color": "#00FBFF",
        "waypoints": [[-29.87,31.03],[-34.36,18.47],[-15.0,40.0],[5.0,55.0],[2.50,101.20],[10.0,110.0],[31.23,121.47]],
    },
    {
        "name": "DRC → Europe",
        "color": "#FFD700",
        "waypoints": [[-29.87,31.03],[-34.36,18.47],[-10.0,0.0],[10.0,-20.0],[36.0,-5.6],[51.92,4.48]],
    },
    {
        "name": "DRC → China (Lobito Corridor)",
        "color": "#FF9500",
        "waypoints": [[-12.33,13.55],[-22.95,14.51],[-34.36,18.47],[5.0,55.0],[2.50,101.20],[31.23,121.47]],
    },
    {
        "name": "Indonesia → China",
        "color": "#00FF88",
        "waypoints": [[-2.85,121.90],[2.50,110.0],[31.23,121.47]],
    },
    {
        "name": "Canada → Europe",
        "color": "#FF00FB",
        "waypoints": [[47.42,-53.83],[50.0,-30.0],[51.92,4.48]],
    },
]
