from __future__ import annotations
import math
from typing import Any, Optional, Tuple
from core.config import HERO_CONFIG
from core.events import Event, EVENT_HERO_LEVEL_UP, EVENT_HERO_SKILL
from graphics import palette as pal
from gameplay.enemies import Enemy


class HeroUnit:
    """Controllable Royal Paladin champion that intercepts enemies, cleaves in melee, levels up, and casts Holy Judgment."""

    def __init__(self, spawn_pos: Tuple[float, float]) -> None:
        self.name: str = str(HERO_CONFIG["name"])
        self.title: str = str(HERO_CONFIG["title"])
        self.max_level: int = int(HERO_CONFIG["max_level"])
        self.xp_thresholds = list(HERO_CONFIG["xp_thresholds"])

        self.level: int = 1
        self.xp: int = 0
        self.x: float = float(spawn_pos[0])
        self.y: float = float(spawn_pos[1])
        self.rally_x: float = float(spawn_pos[0])
        self.rally_y: float = float(spawn_pos[1])
        self.rally_indicator_ms: float = 0.0

        self.hp_max: float = float(HERO_CONFIG["base_hp"])
        self.hp: float = self.hp_max
        self.alive: bool = True
        self.respawn_max_ms: float = float(HERO_CONFIG["respawn_time_ms"])
        self.respawn_timer_ms: float = 0.0

        self.attack_cd_ms: float = 0.0
        self.skill_max_cd_ms: float = float(HERO_CONFIG["skill"]["cooldown_ms"])
        self.skill_cd_ms: float = 0.0
        self.duel_tick_ms: float = 0.0

        self.walk_timer_ms: float = 0.0
        self.walk_frame: int = 0
        self.attack_anim_ms: float = 0.0
        self.attack_frame: int = 0
        self.hit_flash_ms: float = 0.0
        self.facing_left: bool = True
        self.engaged_enemy: Optional[Enemy] = None
        self.marching_to_rally: bool = False

    @property
    def pos(self) -> Tuple[float, float]:
        return (self.x, self.y)

    @property
    def attack_damage(self) -> float:
        return float(HERO_CONFIG["base_damage"]) + (self.level - 1) * float(HERO_CONFIG["damage_per_level"])

    @property
    def xp_ratio(self) -> float:
        if self.level >= self.max_level:
            return 1.0
        cur_floor = self.xp_thresholds[self.level - 1]
        nxt_ceil = self.xp_thresholds[self.level]
        return max(0.0, min(1.0, (self.xp - cur_floor) / max(1.0, float(nxt_ceil - cur_floor))))

    def reset(self, spawn_pos: Tuple[float, float]) -> None:
        self.level = 1
        self.xp = 0
        self.x, self.y = float(spawn_pos[0]), float(spawn_pos[1])
        self.rally_x, self.rally_y = float(spawn_pos[0]), float(spawn_pos[1])
        self.rally_indicator_ms = 0.0
        self.hp_max = float(HERO_CONFIG["base_hp"])
        self.hp = self.hp_max
        self.alive = True
        self.respawn_timer_ms = 0.0
        self.attack_cd_ms = 0.0
        self.skill_cd_ms = 0.0
        self.engaged_enemy = None
        self.marching_to_rally = False
        self.facing_left = True

    def set_rally_point(self, pos: Tuple[float, float]) -> None:
        self.rally_x = float(pos[0])
        self.rally_y = float(pos[1])
        self.rally_indicator_ms = 1800.0
        self.engaged_enemy = None
        self.marching_to_rally = True
        if self.rally_x < self.x - 2.0:
            self.facing_left = True
        elif self.rally_x > self.x + 2.0:
            self.facing_left = False

    def gain_xp(self, amount: int, game_scene: Any) -> None:
        if self.level >= self.max_level:
            return
        self.xp += max(1, int(amount))
        while self.level < self.max_level and self.xp >= self.xp_thresholds[self.level]:
            self.level += 1
            self.hp_max = float(HERO_CONFIG["base_hp"]) + (self.level - 1) * float(HERO_CONFIG["hp_per_level"])
            self.hp = self.hp_max
            game_scene.particles.spawn_build_sparkles(self.pos, pal.GOLD_SHINE)
            game_scene.particles.add_floating_text(
                (self.x, self.y - 24 * game_scene.ui_scale),
                f"HERO LEVEL UP! (Lv.{self.level})",
                pal.GOLD_SHINE,
                big=True,
            )
            game_scene.ev_manager.post(Event(EVENT_HERO_LEVEL_UP, data={"level": self.level}))

    def cast_holy_judgment(self, game_scene: Any) -> bool:
        if not self.alive or self.skill_cd_ms > 0.0:
            return False

        s = game_scene.ui_scale
        sk = HERO_CONFIG["skill"]
        self.skill_cd_ms = self.skill_max_cd_ms

        # Choose strike center: engaged enemy, nearest enemy within 240px, or Hero position
        tx, ty = self.x, self.y
        if self.engaged_enemy is not None and self.engaged_enemy.alive:
            tx, ty = self.engaged_enemy.x, self.engaged_enemy.y
        else:
            nearby = [
                e for e in game_scene.enemies
                if e.alive and math.hypot(e.x - self.x, e.y - self.y) <= 240.0 * s
            ]
            if nearby:
                best = max(nearby, key=lambda e: e.dist_traveled)
                tx, ty = best.x, best.y

        # Self heal
        heal = float(sk["self_heal"]) + (self.level - 1) * 15.0
        self.hp = min(self.hp_max, self.hp + heal)
        self.attack_anim_ms = 360.0

        # AoE Holy Strike
        rad = float(sk["radius"]) * s
        dmg_raw = float(sk["base_damage"]) + (self.level - 1) * float(sk["damage_per_level"])
        game_scene.world_fx.add_holy_sigil((tx, ty), rad)
        game_scene.particles.spawn_build_sparkles((tx, ty), pal.GOLD_SHINE)
        game_scene.particles.spawn_explosion((tx, ty), rad * 0.85)
        game_scene.particles.add_floating_text(
            (tx, ty - 22 * s),
            "HOLY JUDGMENT!",
            pal.GOLD_SHINE,
            big=True,
        )
        game_scene.trigger_shake(4.5, 220.0)
        game_scene.ev_manager.post(Event(EVENT_HERO_SKILL, data={"pos": (tx, ty)}))

        for e in list(game_scene.enemies):
            if e.alive and math.hypot(e.x - tx, e.y - ty) <= rad:
                dmg = e.take_damage(dmg_raw, "magic")
                e.apply_slow(float(sk["slow_factor"]), float(sk["slow_duration_ms"]))
                game_scene.on_enemy_damaged(e, dmg, is_crit=True, color=pal.GOLD_SHINE)
        self.gain_xp(12, game_scene)
        return True

    def update(self, dt_ms: float, game_scene: Any) -> None:
        s = game_scene.ui_scale
        dt_s = dt_ms / 1000.0

        if self.skill_cd_ms > 0.0:
            self.skill_cd_ms = max(0.0, self.skill_cd_ms - dt_ms)
        if self.rally_indicator_ms > 0.0:
            self.rally_indicator_ms = max(0.0, self.rally_indicator_ms - dt_ms)
        if self.hit_flash_ms > 0.0:
            self.hit_flash_ms = max(0.0, self.hit_flash_ms - dt_ms)
        if self.attack_cd_ms > 0.0:
            self.attack_cd_ms = max(0.0, self.attack_cd_ms - dt_ms)

        if self.attack_anim_ms > 0.0:
            self.attack_anim_ms = max(0.0, self.attack_anim_ms - dt_ms)
            self.attack_frame = 1 if self.attack_anim_ms > 140.0 else 2
        else:
            self.attack_frame = 0

        # Handle recovery state if knocked out
        if not self.alive:
            self.respawn_timer_ms -= dt_ms
            if self.respawn_timer_ms <= 0.0:
                self.alive = True
                self.hp = self.hp_max
                self.x, self.y = self.rally_x, self.rally_y
                game_scene.particles.spawn_build_sparkles(self.pos, pal.GOLD_SHINE)
                game_scene.particles.add_floating_text(
                    self.pos,
                    f"{self.name} Revived!",
                    pal.GOLD_SHINE,
                    big=True,
                )
            return

        # Passive health regeneration
        regen = float(HERO_CONFIG["hp_regen_per_sec"]) * (1.8 if self.engaged_enemy is None else 0.6)
        self.hp = min(self.hp_max, self.hp + regen * dt_s)

        move_spd = float(HERO_CONFIG["move_speed"]) * s
        aggro_r = float(HERO_CONFIG["aggro_radius"]) * s
        atk_r = float(HERO_CONFIG["attack_range"]) * s

        # 1. If explicitly marching to a newly clicked rally point, move there first
        if self.marching_to_rally:
            dx = self.rally_x - self.x
            dy = self.rally_y - self.y
            dist = math.hypot(dx, dy)
            if dist <= max(8.0 * s, move_spd * dt_s):
                self.x, self.y = self.rally_x, self.rally_y
                self.marching_to_rally = False
            else:
                self._step_toward(self.rally_x, self.rally_y, move_spd * 1.15 * dt_s, dt_ms)
            return

        # 2. Validate or acquire an enemy within aggro radius of the rally point
        if (
            self.engaged_enemy is None
            or not self.engaged_enemy.alive
            or math.hypot(self.engaged_enemy.x - self.rally_x, self.engaged_enemy.y - self.rally_y) > aggro_r * 1.35
        ):
            candidates = [
                e for e in game_scene.enemies
                if e.alive and math.hypot(e.x - self.rally_x, e.y - self.rally_y) <= aggro_r
            ]
            if candidates:
                self.engaged_enemy = min(candidates, key=lambda e: math.hypot(e.x - self.x, e.y - self.y))
            else:
                self.engaged_enemy = None

        # 3. Engage enemy in melee or return to rally post
        if self.engaged_enemy is not None and self.engaged_enemy.alive:
            tgt = self.engaged_enemy
            dx = tgt.x - self.x
            dy = tgt.y - self.y
            dist = math.hypot(dx, dy)
            if dx < -2.0:
                self.facing_left = True
            elif dx > 2.0:
                self.facing_left = False

            if dist > atk_r:
                self._step_toward(tgt.x, tgt.y, move_spd * dt_s, dt_ms)
            else:
                # Hold & duel the enemy! Slow enemy movement while blocked by Paladin
                tgt.apply_slow(0.72, 260.0)
                self.duel_tick_ms += dt_ms
                if self.duel_tick_ms >= 900.0:
                    self.duel_tick_ms = 0.0
                    chip_dmg = (14.0 if tgt.boss else 5.5)
                    self.hp -= chip_dmg
                    self.hit_flash_ms = 90.0
                    if self.hp <= 0.0:
                        self.hp = 0.0
                        self.alive = False
                        self.engaged_enemy = None
                        self.respawn_timer_ms = self.respawn_max_ms
                        game_scene.particles.add_floating_text(
                            self.pos,
                            "Hero Recovering (10s)...",
                            pal.UI_RED,
                            big=True,
                        )
                        return

                if self.attack_cd_ms <= 0.0:
                    self._perform_melee_cleave(game_scene, tgt)
        else:
            # Return to rally post if drifted away
            dist_rally = math.hypot(self.rally_x - self.x, self.rally_y - self.y)
            if dist_rally > 6.0 * s:
                self._step_toward(self.rally_x, self.rally_y, move_spd * dt_s, dt_ms)
            else:
                self.walk_frame = 0

    def _step_toward(self, tx: float, ty: float, step: float, dt_ms: float) -> None:
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist <= 0.001:
            return
        if dx < -1.5:
            self.facing_left = True
        elif dx > 1.5:
            self.facing_left = False
        if dist <= step:
            self.x, self.y = tx, ty
        else:
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step
        self.walk_timer_ms += dt_ms
        if self.walk_timer_ms >= 115.0:
            self.walk_timer_ms = 0.0
            self.walk_frame = (self.walk_frame + 1) % 4

    def _perform_melee_cleave(self, game_scene: Any, primary_target: Enemy) -> None:
        s = game_scene.ui_scale
        self.attack_cd_ms = float(HERO_CONFIG["attack_cooldown_ms"])
        self.attack_anim_ms = 260.0
        cleave_r = float(HERO_CONFIG["cleave_radius"]) * s
        base_dmg = self.attack_damage

        # Primary strike
        dmg = primary_target.take_damage(base_dmg, "physical")
        game_scene.particles.spawn_hit(primary_target.pos, pal.GOLD_SHINE, count=6)
        game_scene.on_enemy_damaged(primary_target, dmg, is_crit=(self.level >= 4), color=pal.GOLD_SHINE)

        # Cleave nearby enemies
        for e in list(game_scene.enemies):
            if e is not primary_target and e.alive:
                if math.hypot(e.x - primary_target.x, e.y - primary_target.y) <= cleave_r:
                    c_dmg = e.take_damage(base_dmg * 0.60, "physical")
                    game_scene.on_enemy_damaged(e, c_dmg, is_crit=False, color=pal.GOLD_LIGHT)

        self.gain_xp(5, game_scene)

