from __future__ import annotations
import math
from typing import Protocol, Dict, List, Any, Optional


class TargetingStrategy(Protocol):
    def select_target(self, engine: Any, tower: Dict[str, Any], enemies: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]: ...


class NearestTarget:
    def select_target(self, engine: Any, tower: Dict[str, Any], enemies: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not enemies:
            return None
        tx, ty = tower['pos']
        best = None
        best_d = float('inf')
        for e in enemies:
            dx = e['pos'][0] - tx; dy = e['pos'][1] - ty
            d2 = dx*dx + dy*dy
            if d2 < best_d:
                best_d = d2; best = e
        return best


class FirstInList:
    def select_target(self, engine: Any, tower: Dict[str, Any], enemies: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        return enemies[0] if enemies else None

