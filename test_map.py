from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
t = env.get_template('map_section.html')
geo = {
    'mines': [{'name': 'Test', 'lat': 0, 'lng': 0, 'country': 'X', 'operator': 'Y', 'type': 'mine'}],
    'refineries': [],
    'ports': [],
    'chokepoints': [],
    'routes': [{'name': 'TestRoute', 'color': '#fff', 'weight': 2, 'waypoints': [[0,0],[1,1]]}]
}
result = t.render(geo=geo)
print('HAS _mapMines:', '_mapMines' in result)
print('HAS polyline:', 'polyline' in result)
print('HAS _mapRoutes:', '_mapRoutes' in result)