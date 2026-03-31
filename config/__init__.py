"""
config/commodities/__init__.py
Commodity registry.
Import all commodity modules here. To add a new commodity,
create a new file in this folder and add it to REGISTRY.
"""

from config.commodities import cobalt
from config.commodities import coffee

# ─────────────────────────────────────────────
# REGISTRY
# Add new commodities here as you create them.
# Each module must expose: COMMODITY, PRODUCING_REGIONS,
# RISK_CATEGORIES, LINKED_STOCKS
# ─────────────────────────────────────────────
REGISTRY = {
    "Cobalt": cobalt,
    "Coffee": coffee,
}


def get_commodity(name: str):
    """Get a commodity module by name."""
    return REGISTRY.get(name)


def list_commodities() -> list[str]:
    """List all available commodity names."""
    return list(REGISTRY.keys())
