from __future__ import annotations
import math
import random
from typing import Tuple
from core.config import ENEMY_DEFINITIONS
from gameplay.path import RoadPath


class Enemy:
    """Represents a fantasy enemy unit marching along the RoadPath toward the Royal Castle."""

    def __init__(
        self,
        enemy_type: str,
        road: RoadPath,
        hp_mult: float = 1.0,
        speed_mult: float = 1.0,
        gold_mult: float = 1.0,
    ) -> None:
        cfg = ENEMY_DEFINITIONS.get(enemy_type, ENEMY_DEFINITIONS["goblin"])
        self.enemy_type = enemy_type
        self.name = cfg["name"]
        self.hp_max = max(1.0, float(int(cfg["hp"] * hp_mult)))
        self.hp = self.hp_max
        self.base_speed = float(cfg["speed"]) * speed_mult
        self.armor = float(cfg.get("armor", 0.0))
        self.magic_res = float(cfg.get("magic_res", 0.0))
        self.reward = max(1, int(round(cfg["reward"] * gold_mult)))
        self.castle_damage = int(cfg["castle_damage"])
        self.boss = bool(cfg.get("boss", False))

        self.dist_traveled: float = 0.0
        self.lane_offset: float = 0.0 if self.boss else random.uniform(-9.0, 9.0)
        x0, y0, ang = road.get_point_at_distance(0.0)
        self.x: float = x0
        self.y: float = y0
        self.facing_left: bool = False

        # Animation & Status Effects
        self.anim_timer_ms: float = 0.0
        self.walk_frame: int = random.randint(0, 3)
        self.hit_flash_ms: float = 0.0
        self.slow_timer_ms: float = 0.0
        self.slow_factor: float = 0.0
        self.burn_timer_ms: float = 0.0
        self.burn_dps: float = 0.0
        self.alive: bool = True
        self.reached_castle: bool = False
        self.boss_phase: int = 0

    @property
    def pos(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def apply_slow(self, factor: float, duration_ms: float) -> None:
        # Bosses resist 40% of slow potency
        effective = factor * (0.60 if self.boss else 1.0)
        if effective >= self.slow_factor or self.slow_timer_ms <= 0:
            self.slow_factor = max(0.0, min(0.80, effective))
        self.slow_timer_ms = max(self.slow_timer_ms, float(duration_ms))

    def apply_burn(self, dps: float, duration_ms: float) -> None:
        self.burn_dps = max(self.burn_dps, float(dps))
        self.burn_timer_ms = max(self.burn_timer_ms, float(duration_ms))

    def take_damage(self, amount: float, damage_type: str = "physical") -> float:
        if not self.alive:
            return 0.0
        mult = 1.0
        if damage_type == "physical":
            mult = max(0.15, 1.0 - self.armor)
        elif damage_type == "explosive":
            mult = max(0.25, 1.0 - self.armor * 0.45)
        elif damage_type == "magic":
            mult = max(0.20, 1.0 - self.magic_res)
        actual = max(1.0, amount * mult)
        self.hp -= actual
        self.hit_flash_ms = 110.0

        # Boss Enrage Phases
        if self.boss and self.hp > 0:
            ratio = self.hp / self.hp_max
            if ratio < 0.60 and self.boss_phase < 1:
                self.boss_phase = 1
                self.base_speed *= 1.15
            elif ratio < 0.30 and self.boss_phase < 2:
                self.boss_phase = 2
                self.base_speed *= 1.18

        if self.hp <= 0:
            self.hp = 0.0
            self.alive = False
        return actual

    def update(self, dt_ms: float, road: RoadPath) -> None:
        if not self.alive:
            return

        if self.hit_flash_ms > 0:
            self.hit_flash_ms = max(0.0, self.hit_flash_ms - dt_ms)

        if self.slow_timer_ms > 0:
            self.slow_timer_ms = max(0.0, self.slow_timer_ms - dt_ms)
            if self.slow_timer_ms <= 0:
                self.slow_factor = 0.0

        if self.burn_timer_ms > 0:
            self.burn_timer_ms = max(0.0, self.burn_timer_ms - dt_ms)
            self.hp -= self.burn_dps * (dt_ms / 1000.0)
            if self.hp <= 0:
                self.hp = 0.0
                self.alive = False
                return

        spd = self.base_speed * (1.0 - self.slow_factor)
        self.dist_traveled += spd * (dt_ms / 1000.0)

        if self.dist_traveled >= road.total_length:
            self.reached_castle = True
            self.alive = False
            return

        px, py, ang = road.get_point_at_distance(self.dist_traveled)
        # Apply perpendicular lane offset so squads look natural
        perp_rad = math.radians(ang + 90.0)
        self.x = px + math.cos(perp_rad) * self.lane_offset
        self.y = py + math.sin(perp_rad) * self.lane_offset
        self.facing_left = abs(ang) > 95.0

        # Walk animation cadence
        anim_interval = 140.0 if self.slow_timer_ms <= 0 else 220.0
        self.anim_timer_ms += dt_ms
        if self.anim_timer_ms >= anim_interval:
            self.anim_timer_ms -= anim_interval
            self.walk_frame = (self.walk_frame + 1) % 4

