from __future__ import annotations
from typing import Dict, Any, Tuple, List


class BulletPool:
    def __init__(self, capacity: int = 256) -> None:
        self.capacity = capacity
        self._pool: List[Dict[str, Any]] = []

    def acquire(self, pos: Tuple[int, int], target: Dict[str, Any], speed: float) -> Dict[str, Any]:
        if self._pool:
            b = self._pool.pop()
            b['pos'] = [float(pos[0]), float(pos[1])]
            b['target'] = target
            b['speed'] = float(speed)
            return b
        return {'pos': [float(pos[0]), float(pos[1])], 'target': target, 'speed': float(speed)}

    def release(self, bullet: Dict[str, Any]) -> None:
        if len(self._pool) < self.capacity:
            self._pool.append(bullet)

