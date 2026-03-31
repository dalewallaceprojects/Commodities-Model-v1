from config.commodities import cobalt
from config.commodities import coffee

REGISTRY = {
    "Cobalt": cobalt,
    "Coffee": coffee,
}

def get_commodity(name):
    return REGISTRY.get(name)

def list_commodities():
    return list(REGISTRY.keys())
