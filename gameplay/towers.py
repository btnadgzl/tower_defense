from __future__ import annotations
import math
import random
from typing import Tuple, List, Optional, Dict, Any
from core.config import TOWER_DEFINITIONS
from gameplay.strategy import STRATEGIES, TargetingStrategy
from gameplay.enemies import Enemy
from gameplay.projectiles import LightningBoltVisual


class Tower:
    """Represents a fantasy defense tower built on a tactical BuildSlot."""

    def __init__(self, slot_index: int, pos: Tuple[int, int], tower_type: str) -> None:
        self.slot_index = slot_index
        self.pos = pos
        self.tower_type = tower_type
        self.level = 1
        self.strategy_idx = 0
        self.cooldown_ms: float = 0.0
        self.angle_deg: float = 180.0
        self.recoil_ms: float = 0.0
        self.anim_timer_ms: float = 0.0
        self.anim_step: int = 0
        self.total_invested: int = 0
        self._apply_level_stats(1)

    def _apply_level_stats(self, lvl: int) -> None:
        t_cfg = TOWER_DEFINITIONS[self.tower_type]
        l_cfg: Dict[str, Any] = t_cfg["levels"][lvl - 1]
        self.level = lvl
        self.name = t_cfg["name"]
        self.damage_type = t_cfg["damage_type"]
        self.cost = int(l_cfg["cost"])
        self.total_invested += self.cost
        self.damage = float(l_cfg["damage"])
        self.range = float(l_cfg["range"])
        self.fire_rate_ms = float(l_cfg["fire_rate_ms"])
        self.proj_speed = float(l_cfg["proj_speed"])
        self.splash_radius = float(l_cfg.get("splash_radius", 0.0))
        self.slow_factor = float(l_cfg.get("slow_factor", 0.0))
        self.slow_duration_ms = float(l_cfg.get("slow_duration_ms", 0.0))
        self.crit_chance = float(l_cfg.get("crit_chance", 0.0))
        self.chain_targets = int(l_cfg.get("chain_targets", 0))
        self.chain_range = float(l_cfg.get("chain_range", 0.0))

    @property
    def strategy(self) -> TargetingStrategy:
        return STRATEGIES[self.strategy_idx % len(STRATEGIES)]

    def cycle_strategy(self) -> TargetingStrategy:
        self.strategy_idx = (self.strategy_idx + 1) % len(STRATEGIES)
        return self.strategy

    def can_upgrade(self) -> bool:
        return self.level < len(TOWER_DEFINITIONS[self.tower_type]["levels"])

    def next_upgrade_cost(self) -> int:
        if not self.can_upgrade():
            return 0
        return int(TOWER_DEFINITIONS[self.tower_type]["levels"][self.level]["cost"])

    def upgrade(self) -> bool:
        if not self.can_upgrade():
            return False
        self._apply_level_stats(self.level + 1)
        return True

    def get_sell_value(self) -> int:
        return max(10, int(round(self.total_invested * 0.75)))

    def find_target(self, enemies: List[Enemy], ui_scale: float = 1.0) -> Optional[Enemy]:
        tx, ty = self.pos
        eff_range = self.range * ui_scale
        r2 = eff_range * eff_range
        in_range = [
            e for e in enemies
            if e.alive and ((e.x - tx) ** 2 + (e.y - ty) ** 2) <= r2
        ]
        if not in_range:
            return None
        return self.strategy.select_target(self, in_range)

    def update(self, dt_ms: float, game_scene: Any) -> None:
        self.cooldown_ms = max(0.0, self.cooldown_ms - dt_ms)
        self.recoil_ms = max(0.0, self.recoil_ms - dt_ms)
        self.anim_timer_ms += dt_ms
        if self.anim_timer_ms >= 220.0:
            self.anim_timer_ms -= 220.0
            self.anim_step = (self.anim_step + 1) % 4

        target = self.find_target(game_scene.enemies, game_scene.ui_scale)
        if target is not None:
            dx = target.x - self.pos[0]
            dy = target.y - self.pos[1]
            self.angle_deg = math.degrees(math.atan2(dy, dx))

            if self.cooldown_ms <= 0.0:
                self._fire_at(target, game_scene)
                self.cooldown_ms = self.fire_rate_ms
                self.recoil_ms = 140.0

    def _fire_at(self, target: Enemy, game_scene: Any) -> None:
        sx, sy = self.pos[0], self.pos[1] - int(12 * game_scene.ui_scale)

        if self.tower_type == "lightning":
            # Instant Chain Lightning across targets
            hit_chain: List[Enemy] = [target]
            pts: List[Tuple[float, float]] = [(float(sx), float(sy)), (target.x, target.y)]
            cur_dmg = self.damage
            actual = target.take_damage(cur_dmg, "magic")
            game_scene.on_enemy_damaged(target, actual, is_crit=False, color=(215, 145, 255))

            cur_enemy = target
            for _ in range(self.chain_targets - 1):
                best_next = None
                best_d = (self.chain_range * game_scene.ui_scale) ** 2
                for cand in game_scene.enemies:
                    if cand.alive and cand not in hit_chain:
                        d2 = (cand.x - cur_enemy.x) ** 2 + (cand.y - cur_enemy.y) ** 2
                        if d2 <= best_d:
                            best_d = d2
                            best_next = cand
                if best_next is None:
                    break
                hit_chain.append(best_next)
                pts.append((best_next.x, best_next.y))
                cur_dmg *= 0.75
                dmg_dealt = best_next.take_damage(cur_dmg, "magic")
                game_scene.on_enemy_damaged(best_next, dmg_dealt, is_crit=False, color=(215, 145, 255))
                cur_enemy = best_next

            game_scene.lightning_arcs.append(LightningBoltVisual(pts, ttl_ms=210.0))
            game_scene.notify_tower_fire(self.tower_type, target.pos)
            return

        # Projectile-based towers: archer, artillery, frost
        kind_map = {
            "archer": "arrow",
            "artillery": "bomb",
            "frost": "frost",
        }
        kind = kind_map.get(self.tower_type, "arrow")
        proj = game_scene.proj_pool.acquire(
            kind=kind,
            start_pos=(sx, sy),
            target=target,
            speed=self.proj_speed * game_scene.ui_scale,
            damage=self.damage,
            damage_type=self.damage_type,
            splash_radius=self.splash_radius * game_scene.ui_scale,
            slow_factor=self.slow_factor,
            slow_duration_ms=self.slow_duration_ms,
            crit_chance=self.crit_chance,
        )
        game_scene.projectiles.append(proj)
        game_scene.notify_tower_fire(self.tower_type, target.pos)

