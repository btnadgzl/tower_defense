from __future__ import annotations
from typing import Dict, Tuple, Any


def create_tower(pos: Tuple[int, int], range_px: int = 300, fire_rate_ms: int = 300) -> Dict[str, Any]:
    return {
        'pos': (pos[0], pos[1]),
        'range': int(range_px),
        'cooldown': 0,
        'fire_rate': int(fire_rate_ms),
    }


def create_enemy(pos: Tuple[int, int], hp: int, speed: float, boss: bool = False) -> Dict[str, Any]:
    return {
        'pos': [float(pos[0]), float(pos[1])],
        'hp': int(hp),
        'speed': float(speed),
        'boss': bool(boss),
        'knockback': None,
    }
