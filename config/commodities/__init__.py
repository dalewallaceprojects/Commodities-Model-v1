"""
config/commodities/__init__.py
Commodity registry.
"""

from config.commodities import cobalt
from config.commodities import coffee

REGISTRY = {
    "Cobalt": cobalt,
    "Coffee": coffee,
}

def get_commodity(name: str):
    return REGISTRY.get(name)

def list_commodities() -> list[str]:
    return list(REGISTRY.keys())
