from __future__ import annotations
from typing import Protocol, List, Any, Optional


class TargetingStrategy(Protocol):
    name: str
    short_label: str

    def select_target(self, tower: Any, candidates: List[Any]) -> Optional[Any]: ...


class FirstOnPath:
    """Targets the enemy furthest along the road (closest to the Royal Castle)."""
    name = "first"
    short_label = "First"

    def select_target(self, tower: Any, candidates: List[Any]) -> Optional[Any]:
        if not candidates:
            return None
        return max(candidates, key=lambda e: e.dist_traveled)


class StrongestTarget:
    """Targets the enemy with the highest current HP."""
    name = "strongest"
    short_label = "Strongest"

    def select_target(self, tower: Any, candidates: List[Any]) -> Optional[Any]:
        if not candidates:
            return None
        return max(candidates, key=lambda e: (e.hp, e.dist_traveled))


class WeakestTarget:
    """Targets the enemy with the lowest current HP."""
    name = "weakest"
    short_label = "Weakest"

    def select_target(self, tower: Any, candidates: List[Any]) -> Optional[Any]:
        if not candidates:
            return None
        return min(candidates, key=lambda e: (e.hp, -e.dist_traveled))


class NearestTarget:
    """Targets the enemy physically closest to the tower."""
    name = "nearest"
    short_label = "Nearest"

    def select_target(self, tower: Any, candidates: List[Any]) -> Optional[Any]:
        if not candidates:
            return None
        tx, ty = tower.pos
        return min(
            candidates,
            key=lambda e: (e.x - tx) ** 2 + (e.y - ty) ** 2,
        )


STRATEGIES = [
    FirstOnPath(),
    StrongestTarget(),
    WeakestTarget(),
    NearestTarget(),
]
