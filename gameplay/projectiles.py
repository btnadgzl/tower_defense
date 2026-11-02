from __future__ import annotations
import math
import random
from typing import List, Tuple, Optional, Any
from gameplay.enemies import Enemy


class Projectile:
    """Pooled projectile supporting homing arrows, parabolic AoE bombs, and frost shards."""

    def __init__(self) -> None:
        self.active: bool = False
        self.kind: str = "arrow"
        self.x: float = 0.0
        self.y: float = 0.0
        self.start_x: float = 0.0
        self.start_y: float = 0.0
        self.target_x: float = 0.0
        self.target_y: float = 0.0
        self.target: Optional[Enemy] = None
        self.speed: float = 450.0
        self.damage: float = 15.0
        self.damage_type: str = "physical"
        self.angle_deg: float = 0.0
        self.splash_radius: float = 0.0
        self.slow_factor: float = 0.0
        self.slow_duration_ms: float = 0.0
        self.crit_chance: float = 0.0
        # Parabolic flight tracking
        self.flight_elapsed: float = 0.0
        self.flight_duration: float = 0.5
        self.z_height: float = 0.0

    def reset(
        self,
        kind: str,
        start_pos: Tuple[float, float],
        target: Enemy,
        speed: float,
        damage: float,
        damage_type: str = "physical",
        splash_radius: float = 0.0,
        slow_factor: float = 0.0,
        slow_duration_ms: float = 0.0,
        crit_chance: float = 0.0,
    ) -> "Projectile":
        self.active = True
        self.kind = kind
        self.x, self.y = float(start_pos[0]), float(start_pos[1])
        self.start_x, self.start_y = self.x, self.y
        self.target = target
        self.target_x, self.target_y = target.x, target.y
        self.speed = float(speed)
        self.damage = float(damage)
        self.damage_type = damage_type
        self.splash_radius = float(splash_radius)
        self.slow_factor = float(slow_factor)
        self.slow_duration_ms = float(slow_duration_ms)
        self.crit_chance = float(crit_chance)
        self.flight_elapsed = 0.0
        dist = max(20.0, math.hypot(self.target_x - self.start_x, self.target_y - self.start_y))
        self.flight_duration = dist / max(80.0, self.speed)
        self.z_height = 0.0
        self.angle_deg = math.degrees(math.atan2(self.target_y - self.y, self.target_x - self.x))
        return self


class ProjectilePool:
    """Object pool for Projectile instances to avoid runtime allocation."""

    def __init__(self, capacity: int = 256) -> None:
        self.capacity = capacity
        self._pool: List[Projectile] = [Projectile() for _ in range(64)]

    def acquire(self, **kwargs: Any) -> Projectile:
        proj = self._pool.pop() if self._pool else Projectile()
        return proj.reset(**kwargs)

    def release(self, proj: Projectile) -> None:
        proj.active = False
        proj.target = None
        if len(self._pool) < self.capacity:
            self._pool.append(proj)


class LightningBoltVisual:
    """Short-lived jagged pixel lightning arc between chain points."""

    def __init__(self, points: List[Tuple[float, float]], ttl_ms: float = 200.0) -> None:
        self.segments: List[List[Tuple[int, int]]] = []
        self.ttl_ms = ttl_ms
        self.max_ttl_ms = ttl_ms
        for i in range(len(points) - 1):
            p0 = points[i]
            p1 = points[i + 1]
            self.segments.append(self._jagged_line(p0, p1))

    @staticmethod
    def _jagged_line(p0: Tuple[float, float], p1: Tuple[float, float], steps: int = 6) -> List[Tuple[int, int]]:
        pts: List[Tuple[int, int]] = [(int(p0[0]), int(p0[1]))]
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        for s in range(1, steps):
            t = s / float(steps)
            jx = p0[0] + dx * t + random.uniform(-9.0, 9.0)
            jy = p0[1] + dy * t + random.uniform(-9.0, 9.0)
            pts.append((int(jx), int(jy)))
        pts.append((int(p1[0]), int(p1[1])))
        return pts

