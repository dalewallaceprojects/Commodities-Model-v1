"""
config/commodities/coffee_geo.py
Geographic data for coffee supply chain mapping.
"""

MINES = [
    # Using "mines" for plantations/growing regions to keep the data structure consistent
    {"name": "Minas Gerais", "lat": -19.92, "lng": -43.94, "country": "Brazil", "operator": "Multiple farms"},
    {"name": "São Paulo (Mogiana)", "lat": -22.20, "lng": -47.30, "country": "Brazil", "operator": "Multiple farms"},
    {"name": "Espírito Santo", "lat": -20.32, "lng": -40.34, "country": "Brazil", "operator": "Robusta region"},
    {"name": "Dak Lak (Central Highlands)", "lat": 12.67, "lng": 108.05, "country": "Vietnam", "operator": "Robusta heartland"},
    {"name": "Lam Dong", "lat": 11.94, "lng": 108.44, "country": "Vietnam", "operator": "Arabica & Robusta"},
    {"name": "Huila", "lat": 2.53, "lng": -75.53, "country": "Colombia", "operator": "Arabica (washed)"},
    {"name": "Antioquia", "lat": 6.70, "lng": -75.50, "country": "Colombia", "operator": "Arabica (washed)"},
    {"name": "Sumatra (Mandheling)", "lat": 2.50, "lng": 99.05, "country": "Indonesia", "operator": "Arabica/Robusta"},
    {"name": "Java", "lat": -7.61, "lng": 110.20, "country": "Indonesia", "operator": "Arabica estates"},
    {"name": "Sidamo/Yirgacheffe", "lat": 6.16, "lng": 38.21, "country": "Ethiopia", "operator": "Arabica birthplace"},
    {"name": "Jimma", "lat": 7.67, "lng": 36.83, "country": "Ethiopia", "operator": "Wild Arabica forests"},
    {"name": "Copán", "lat": 14.84, "lng": -88.45, "country": "Honduras", "operator": "Arabica"},
    {"name": "Mount Elgon", "lat": 1.12, "lng": 34.56, "country": "Uganda", "operator": "Arabica & Robusta"},
    {"name": "Cajamarca", "lat": -7.16, "lng": -78.51, "country": "Peru", "operator": "Arabica (organic)"},
]

REFINERIES = [
    # Roasting/processing hubs
    {"name": "Hamburg (roasting hub)", "lat": 53.55, "lng": 9.99, "country": "Germany"},
    {"name": "Trieste (Illy/Lavazza)", "lat": 45.65, "lng": 13.78, "country": "Italy"},
    {"name": "Ho Chi Minh City", "lat": 10.82, "lng": 106.63, "country": "Vietnam"},
    {"name": "Santos processing", "lat": -23.96, "lng": -46.33, "country": "Brazil"},
    {"name": "Houston (roasters)", "lat": 29.76, "lng": -95.37, "country": "USA"},
    {"name": "Nestlé (Vevey)", "lat": 46.46, "lng": 6.84, "country": "Switzerland"},
    {"name": "Kunshan (Starbucks roastery)", "lat": 31.39, "lng": 120.98, "country": "China"},
    {"name": "Amsterdam (Jacobs Douwe Egberts)", "lat": 52.37, "lng": 4.90, "country": "Netherlands"},
]

PORTS = [
    {"name": "Santos", "lat": -23.96, "lng": -46.33, "country": "Brazil", "role": "World's largest coffee export port"},
    {"name": "Ho Chi Minh City", "lat": 10.82, "lng": 106.63, "country": "Vietnam", "role": "Vietnam's primary coffee export"},
    {"name": "Buenaventura", "lat": 3.88, "lng": -77.02, "country": "Colombia", "role": "Colombia's Pacific export hub"},
    {"name": "Cartagena", "lat": 10.39, "lng": -75.51, "country": "Colombia", "role": "Colombia's Atlantic export hub"},
    {"name": "Djibouti", "lat": 11.59, "lng": 43.15, "country": "Djibouti", "role": "Ethiopian coffee export route"},
    {"name": "Mombasa", "lat": -4.04, "lng": 39.67, "country": "Kenya", "role": "East African coffee export"},
    {"name": "Hamburg", "lat": 53.55, "lng": 9.99, "country": "Germany", "role": "Europe's largest coffee import port"},
    {"name": "New York/New Jersey", "lat": 40.67, "lng": -74.04, "country": "USA", "role": "US East Coast import hub"},
    {"name": "New Orleans", "lat": 29.95, "lng": -90.07, "country": "USA", "role": "US coffee import & ICE warehousing"},
    {"name": "Antwerp", "lat": 51.26, "lng": 4.40, "country": "Belgium", "role": "European green coffee trading"},
]

CHOKEPOINTS = [
    {"name": "Panama Canal", "lat": 9.08, "lng": -79.68},
    {"name": "Suez Canal", "lat": 30.46, "lng": 32.35},
    {"name": "Strait of Malacca", "lat": 2.50, "lng": 101.20},
    {"name": "Bab el-Mandeb", "lat": 12.58, "lng": 43.33},
    {"name": "Cape of Good Hope", "lat": -34.36, "lng": 18.47},
]

ROUTES = [
    {
        "name": "Brazil → Europe",
        "color": "#00FBFF",
        "waypoints": [[-23.96,-46.33],[-10.0,-25.0],[10.0,-20.0],[36.0,-5.6],[53.55,9.99]],
    },
    {
        "name": "Brazil → USA",
        "color": "#FFD700",
        "waypoints": [[-23.96,-46.33],[-5.0,-35.0],[15.0,-60.0],[25.0,-70.0],[40.67,-74.04]],
    },
    {
        "name": "Vietnam → Europe (via Suez)",
        "color": "#FF9500",
        "waypoints": [[10.82,106.63],[2.50,101.20],[5.0,80.0],[12.58,43.33],[30.46,32.35],[36.0,15.0],[53.55,9.99]],
    },
    {
        "name": "Colombia → USA",
        "color": "#00FF88",
        "waypoints": [[3.88,-77.02],[9.08,-79.68],[20.0,-85.0],[25.0,-80.0],[40.67,-74.04]],
    },
    {
        "name": "Ethiopia → Europe",
        "color": "#FF00FB",
        "waypoints": [[11.59,43.15],[12.58,43.33],[30.46,32.35],[36.0,15.0],[53.55,9.99]],
    },
    {
        "name": "Vietnam → USA",
        "color": "#E040FB",
        "waypoints": [[10.82,106.63],[15.0,120.0],[35.0,150.0],[40.0,-160.0],[33.7,-118.2]],
    },
]
