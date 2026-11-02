from __future__ import annotations
import math
import os
import random
import sys
from typing import List, Tuple, Dict, Any, Optional
import pygame

from core.config import (
    BASE_WIDTH,
    BASE_HEIGHT,
    PIXEL_SCALE,
    FPS,
    DIFFICULTY_PROFILES,
    TOWER_DEFINITIONS,
    SPELLS_CONFIG,
    load_settings,
    save_settings,
)
from core.events import (
    Event,
    EventManager,
    EVENT_QUIT,
    EVENT_STATE_CHANGED,
    EVENT_GAME_OVER,
    EVENT_VICTORY,
    EVENT_WAVE_STARTED,
    EVENT_WAVE_CLEARED,
    EVENT_ENEMY_SPAWNED,
    EVENT_ENEMY_KILLED,
    EVENT_ENEMY_REACHED_CASTLE,
    EVENT_TOWER_BUILT,
    EVENT_TOWER_UPGRADED,
    EVENT_TOWER_SOLD,
    EVENT_TOWER_FIRE,
    EVENT_SPELL_CAST,
    EVENT_UI_CLICK,
)
from core.logger import init_logging, get_logger
from graphics import palette as pal
from graphics.pixel_gen import PixelArtGenerator
from graphics.map_baker import bake_pixel_map
from graphics.ui_kit import draw_text_shadow
from gameplay.path import RoadPath, BuildSlot
from gameplay.enemies import Enemy
from gameplay.towers import Tower
from gameplay.projectiles import Projectile, ProjectilePool, LightningBoltVisual
from gameplay.waves import WaveManager
from systems.particles import ParticleSystem
from systems.sound import SoundSystem
from ui.radial_menu import RadialMenu
from ui.hud import GameHUD
from ui.menus import MenuSystem


class TowerDefenseGame:
    """Main engine for Tower Defense 2.0: Royal Guard Tactical Pixel-Art Edition."""

    def __init__(self, ev_manager: EventManager) -> None:
        self.ev_manager = ev_manager
        self.ev_manager.register(self)
        self.running = True

        pygame.init()
        self.base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        self.settings = load_settings(self.base_dir)

        self.width = BASE_WIDTH
        self.height = BASE_HEIGHT
        self.ui_scale = 1.0
        self.pixel_scale = PIXEL_SCALE
        self.fullscreen = bool(self.settings.get("fullscreen", False))
        self.sound_volume = float(self.settings.get("sfx_volume", 0.7))
        self.music_volume = float(self.settings.get("music_volume", 0.5))
        self.sound_enabled = True

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tower Defense II — Royal Guard")
        self.clock = pygame.time.Clock()

        # Procedural Pixel-Art Generator & Set Window Icon
        self.pixel_gen = PixelArtGenerator(pixel_scale=3)
        try:
            icon_srf = self.pixel_gen.get_tower_turret("archer", 3, 0.0, 0)
            pygame.display.set_icon(icon_srf)
        except Exception:
            pass

        # Fonts
        self._init_fonts(1.0)

        # World & Gameplay Systems
        self.road = RoadPath(self.width, self.height)
        self.map_surface: Optional[pygame.Surface] = None
        self.wave_mgr = WaveManager()
        self.proj_pool = ProjectilePool()
        self.particles = ParticleSystem()
        self.radial_menu = RadialMenu()
        self.hud = GameHUD()
        self.menus = MenuSystem()

        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []
        self.lightning_arcs: List[LightningBoltVisual] = []
        self.falling_meteors: List[Dict[str, Any]] = []
        self.hovered_slot: Optional[BuildSlot] = None

        # State & Economy
        self.state = "menu"
        self.settings_return_state = "menu"
        self.game_speed = 1.0
        self.endless_mode = False
        self.coins = 200
        self.score = 0
        self.castle_hp_max = 100.0
        self.castle_hp = 100.0
        self.spell_cooldowns: Dict[str, float] = {"meteor": 0.0, "blizzard": 0.0}

        # Camera Shake & Banners
        self.camera_offset: Tuple[int, int] = (0, 0)
        self.shake_timer_ms: float = 0.0
        self.shake_strength: float = 0.0
        self.banner_text: str = ""
        self.banner_timer_ms: float = 0.0

        self.apply_display_mode()
        self.reset_battle()

    def _init_fonts(self, scale: float) -> None:
        ttf_path = os.path.join(self.base_dir, "assets", "counter.ttf")
        s_small = max(13, int(15 * scale))
        s_mid = max(16, int(20 * scale))
        s_big = max(26, int(34 * scale))
        try:
            self.font_small = pygame.font.SysFont("consolas", s_small, bold=True)
            self.font_mid = pygame.font.SysFont("consolas", s_mid, bold=True)
            if os.path.exists(ttf_path):
                self.font_big = pygame.font.Font(ttf_path, s_big)
            else:
                self.font_big = pygame.font.SysFont("consolas", s_big, bold=True)
        except Exception:
            self.font_small = pygame.font.SysFont(None, s_small)
            self.font_mid = pygame.font.SysFont(None, s_mid)
            self.font_big = pygame.font.SysFont(None, s_big)

    def apply_display_mode(self) -> None:
        if self.fullscreen:
            info = pygame.display.Info()
            self.width, self.height = info.current_w, info.current_h
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        else:
            self.width, self.height = BASE_WIDTH, BASE_HEIGHT
            self.screen = pygame.display.set_mode((self.width, self.height))

        sx = self.width / float(BASE_WIDTH)
        sy = self.height / float(BASE_HEIGHT)
        self.ui_scale = min(sx, sy)
        self.pixel_scale = max(2, int(round(3 * self.ui_scale)))
        self.pixel_gen.clear_cache(self.pixel_scale)
        self._init_fonts(self.ui_scale)
        self.road.rebuild(self.width, self.height)
        self.map_surface = bake_pixel_map(
            self.width,
            self.height,
            self.road,
            pixel_scale=max(3, int(round(PIXEL_SCALE * self.ui_scale))),
        )

    def persist_settings(self) -> None:
        save_settings(self.base_dir, self.settings)

    def change_state(self, new_state: str) -> None:
        self.state = new_state
        self.ev_manager.post(Event(EVENT_STATE_CHANGED, data={"state": new_state}))

    def reset_battle(self) -> None:
        diff_key = self.settings.get("difficulty", "normal")
        prof = DIFFICULTY_PROFILES.get(diff_key, DIFFICULTY_PROFILES["normal"])

        self.enemies.clear()
        for p in self.projectiles:
            self.proj_pool.release(p)
        self.projectiles.clear()
        self.lightning_arcs.clear()
        self.falling_meteors.clear()
        self.particles.clear()
        self.radial_menu.close()

        for sl in self.road.slots:
            sl.tower = None

        self.wave_mgr.reset()
        self.coins = int(prof["starting_gold"])
        self.score = 0
        self.castle_hp_max = float(prof["castle_hp"])
        self.castle_hp = self.castle_hp_max
        self.game_speed = 1.0
        self.endless_mode = False
        self.spell_cooldowns = {"meteor": 0.0, "blizzard": 0.0}
        self.banner_text = "BUILD YOUR TOWERS AND PREPARE YOUR DEFENSES!"
        self.banner_timer_ms = 3200.0

    # ------------------------------------------------------------------
    # EVENT BUS & INPUT HANDLING
    # ------------------------------------------------------------------
    def notify(self, event: Event) -> None:
        if event.name == EVENT_QUIT:
            self.persist_settings()
            self.running = False

    def handle_events(self) -> None:
        mx, my = pygame.mouse.get_pos()

        # Update hovered slot when in playing state
        self.hovered_slot = None
        if self.state == "playing" and not self.radial_menu.is_open:
            for sl in self.road.slots:
                if math.hypot(mx - sl.pos[0], my - sl.pos[1]) <= 34 * self.ui_scale:
                    self.hovered_slot = sl
                    break

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.ev_manager.post(Event(EVENT_QUIT))
            elif ev.type == pygame.KEYDOWN:
                self._handle_keydown(ev.key)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self._handle_left_click(ev.pos)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3:
                if self.radial_menu.is_open:
                    self.radial_menu.close()

    def _handle_keydown(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            if self.state == "playing":
                if self.radial_menu.is_open:
                    self.radial_menu.close()
                else:
                    self.change_state("paused")
            elif self.state == "paused":
                self.change_state("playing")
            elif self.state == "settings":
                self.persist_settings()
                self.change_state(self.settings_return_state)
            return

        if self.state != "playing":
            return

        # Speed toggle [Space]
        if key == pygame.K_SPACE:
            self.game_speed = 2.0 if self.game_speed == 1.0 else 1.0
            self.ev_manager.post(Event(EVENT_UI_CLICK))
        # Call Wave Early [N]
        elif key == pygame.K_n:
            if self.wave_mgr.state == "prep":
                self._call_wave_now()
        # Active Spells [Q] and [W]
        elif key == pygame.K_q:
            self.cast_spell("meteor")
        elif key == pygame.K_w:
            self.cast_spell("blizzard")
        # Radial Menu Keyboard Shortcuts when a slot is open
        elif self.radial_menu.is_open and self.radial_menu.active_slot is not None:
            slot = self.radial_menu.active_slot
            if slot.tower is None:
                key_map = {
                    pygame.K_1: "archer",
                    pygame.K_2: "artillery",
                    pygame.K_3: "frost",
                    pygame.K_4: "lightning",
                }
                if key in key_map:
                    self._try_build_tower(slot, key_map[key])
            else:
                if key == pygame.K_u:
                    self._try_upgrade_tower(slot)
                elif key == pygame.K_t:
                    self._cycle_tower_strategy(slot)
                elif key in (pygame.K_s, pygame.K_BACKSPACE):
                    self._sell_tower(slot)

    def _handle_left_click(self, pos: Tuple[int, int]) -> None:
        if self.state == "menu":
            self.menus.handle_main_menu_click(pos, self)
            return
        if self.state == "settings":
            self.menus.handle_settings_click(pos, self)
            return
        if self.state in ("paused", "game_over", "victory"):
            self.menus.handle_overlay_click(pos, self)
            return
        if self.state != "playing":
            return

        # 1. Check HUD Buttons first
        if self.hud.call_wave_rect.collidepoint(pos) and self.wave_mgr.state == "prep":
            self._call_wave_now()
            return
        if self.hud.speed_btn_rect.collidepoint(pos):
            self.game_speed = 2.0 if self.game_speed == 1.0 else 1.0
            self.ev_manager.post(Event(EVENT_UI_CLICK))
            return
        if self.hud.pause_btn_rect.collidepoint(pos):
            self.ev_manager.post(Event(EVENT_UI_CLICK))
            self.change_state("paused")
            return
        if self.hud.meteor_btn_rect.collidepoint(pos):
            self.cast_spell("meteor")
            return
        if self.hud.blizzard_btn_rect.collidepoint(pos):
            self.cast_spell("blizzard")
            return

        # 2. Check open Radial Menu nodes
        if self.radial_menu.is_open and self.radial_menu.active_slot is not None:
            slot = self.radial_menu.active_slot
            for node_key, rect in self.radial_menu.node_rects.items():
                if rect.collidepoint(pos):
                    if slot.tower is None and node_key in TOWER_DEFINITIONS:
                        self._try_build_tower(slot, node_key)
                    elif slot.tower is not None:
                        if node_key == "upgrade":
                            self._try_upgrade_tower(slot)
                        elif node_key == "strategy":
                            self._cycle_tower_strategy(slot)
                        elif node_key == "sell":
                            self._sell_tower(slot)
                    return
            # Clicked outside radial nodes -> close radial menu
            self.radial_menu.close()

        # 3. Check Tactical Build Slots on the map
        for sl in self.road.slots:
            if math.hypot(pos[0] - sl.pos[0], pos[1] - sl.pos[1]) <= 34 * self.ui_scale:
                self.ev_manager.post(Event(EVENT_UI_CLICK))
                self.radial_menu.open_for_slot(sl)
                return

    # ------------------------------------------------------------------
    # TOWER ACTIONS & ACTIVE SPELLS
    # ------------------------------------------------------------------
    def _try_build_tower(self, slot: BuildSlot, tower_type: str) -> None:
        cost = int(TOWER_DEFINITIONS[tower_type]["levels"][0]["cost"])
        if self.coins < cost:
            self.particles.add_floating_text(slot.pos, "Not Enough Gold!", pal.UI_RED)
            return
        self.coins -= cost
        slot.tower = Tower(slot.index, slot.pos, tower_type)
        self.particles.spawn_build_sparkles(slot.pos, TOWER_DEFINITIONS[tower_type]["color"])
        self.particles.add_floating_text(slot.pos, f"-{cost}G", pal.GOLD_SHINE)
        self.ev_manager.post(Event(EVENT_TOWER_BUILT, data={"type": tower_type, "slot": slot.index}))
        self.radial_menu.close()

    def _try_upgrade_tower(self, slot: BuildSlot) -> None:
        tw = slot.tower
        if tw is None or not tw.can_upgrade():
            return
        cost = tw.next_upgrade_cost()
        if self.coins < cost:
            self.particles.add_floating_text(slot.pos, "Not Enough Gold!", pal.UI_RED)
            return
        self.coins -= cost
        tw.upgrade()
        self.particles.spawn_build_sparkles(slot.pos, pal.GOLD_SHINE)
        self.particles.add_floating_text(slot.pos, f"Lv.{tw.level} Upgraded!", pal.GOLD_SHINE, big=True)
        self.ev_manager.post(Event(EVENT_TOWER_UPGRADED, data={"type": tw.tower_type, "level": tw.level}))
        self.radial_menu.close()

    def _cycle_tower_strategy(self, slot: BuildSlot) -> None:
        tw = slot.tower
        if tw is None:
            return
        strat = tw.cycle_strategy()
        self.ev_manager.post(Event(EVENT_UI_CLICK))
        self.particles.add_floating_text(slot.pos, f"Target: {strat.short_label}", pal.UI_CYAN)

    def _sell_tower(self, slot: BuildSlot) -> None:
        tw = slot.tower
        if tw is None:
            return
        refund = tw.get_sell_value()
        self.coins += refund
        slot.tower = None
        self.particles.spawn_build_sparkles(slot.pos, pal.GOLD_MID)
        self.particles.add_floating_text(slot.pos, f"+{refund}G Refund", pal.GOLD_SHINE)
        self.ev_manager.post(Event(EVENT_TOWER_SOLD, data={"refund": refund}))
        self.radial_menu.close()

    def _call_wave_now(self) -> None:
        bonus = self.wave_mgr.start_next_wave()
        if bonus > 0:
            self.coins += bonus
            self.score += bonus * 2
            self.particles.add_floating_text(
                (self.width // 2, int(75 * self.ui_scale)),
                f"Early Wave Bonus: +{bonus} Gold!",
                pal.GOLD_SHINE,
                big=True,
            )
        self.banner_text = f"WAVE {self.wave_mgr.current_wave}: {self.wave_mgr.wave_title.upper()}"
        self.banner_timer_ms = 2600.0
        self.ev_manager.post(Event(EVENT_WAVE_STARTED, data={"wave": self.wave_mgr.current_wave}))

    def cast_spell(self, spell_key: str) -> None:
        if self.spell_cooldowns.get(spell_key, 0.0) > 0.0:
            return
        cfg = SPELLS_CONFIG[spell_key]
        self.spell_cooldowns[spell_key] = float(cfg["cooldown_ms"])
        self.ev_manager.post(Event(EVENT_SPELL_CAST, data={"spell": spell_key}))

        if spell_key == "meteor":
            self.banner_text = "METEOR SHOWER!"
            self.banner_timer_ms = 1800.0
            alive_enemies = sorted(
                [e for e in self.enemies if e.alive],
                key=lambda e: e.dist_traveled,
                reverse=True,
            )
            for i in range(6):
                if i < len(alive_enemies):
                    tx, ty = alive_enemies[i].x, alive_enemies[i].y
                else:
                    d = random.uniform(0.18, 0.82) * self.road.total_length
                    tx, ty, _ = self.road.get_point_at_distance(d)
                self.falling_meteors.append({
                    "x": tx - 140.0 * self.ui_scale,
                    "y": ty - 280.0 * self.ui_scale,
                    "tx": tx,
                    "ty": ty,
                    "delay_ms": i * 160.0,
                    "progress": 0.0,
                    "damage": float(cfg["damage"]),
                    "radius": float(cfg["radius"]) * self.ui_scale,
                })

        elif spell_key == "blizzard":
            self.banner_text = "ROYAL BLIZZARD!"
            self.banner_timer_ms = 1800.0
            heal = float(cfg.get("castle_heal", 15))
            self.castle_hp = min(self.castle_hp_max, self.castle_hp + heal)
            self.particles.add_floating_text(
                self.road.castle_pos,
                f"+{int(heal)} Castle Repaired",
                pal.UI_GREEN,
                big=True,
            )
            for e in list(self.enemies):
                if e.alive:
                    dmg = e.take_damage(float(cfg["damage"]), "magic")
                    e.apply_slow(float(cfg["slow_factor"]), float(cfg["slow_duration_ms"]))
                    self.particles.spawn_frost_nova(e.pos, 38.0 * self.ui_scale)
                    self.on_enemy_damaged(e, dmg, is_crit=False, color=pal.FROST_LIGHT)
            self.trigger_shake(4.0, 260.0)

    # ------------------------------------------------------------------
    # UPDATE LOOP
    # ------------------------------------------------------------------
    def update(self, raw_dt_ms: float) -> None:
        mx, my = pygame.mouse.get_pos()
        self.radial_menu.update(raw_dt_ms, (mx, my))

        if self.state != "playing":
            return

        dt_ms = raw_dt_ms * self.game_speed

        # Update cooldowns & timers
        for k in self.spell_cooldowns:
            if self.spell_cooldowns[k] > 0.0:
                self.spell_cooldowns[k] = max(0.0, self.spell_cooldowns[k] - dt_ms)
        if self.banner_timer_ms > 0.0:
            self.banner_timer_ms = max(0.0, self.banner_timer_ms - raw_dt_ms)

        self._update_waves(dt_ms)
        self._update_meteors(dt_ms)

        # Update Towers
        for sl in self.road.slots:
            if sl.tower is not None:
                sl.tower.update(dt_ms, self)

        # Update Projectiles
        self._update_projectiles(dt_ms)

        # Update Lightning Arcs
        for arc in list(self.lightning_arcs):
            arc.ttl_ms -= dt_ms
            if arc.ttl_ms <= 0:
                self.lightning_arcs.remove(arc)

        # Update Enemies
        for e in list(self.enemies):
            prev_alive = e.alive
            e.update(dt_ms, self.road)
            if prev_alive and not e.alive and not e.reached_castle:
                self._handle_enemy_death(e)
            elif e.reached_castle:
                self.enemies.remove(e)
                self.castle_hp = max(0.0, self.castle_hp - e.castle_damage)
                self.trigger_shake(6.5, 320.0)
                self.particles.spawn_explosion(self.road.castle_pos, 48.0 * self.ui_scale)
                self.particles.add_floating_text(
                    self.road.castle_pos,
                    f"-{e.castle_damage} Castle HP!",
                    pal.UI_RED,
                    big=True,
                )
                self.ev_manager.post(Event(EVENT_ENEMY_REACHED_CASTLE, data={"damage": e.castle_damage}))
                if self.castle_hp <= 0.0:
                    self._record_high_score()
                    self.ev_manager.post(Event(EVENT_GAME_OVER))
                    self.change_state("game_over")
                    return

        self.particles.update(dt_ms)
        self._update_camera_shake(raw_dt_ms)

    def _update_waves(self, dt_ms: float) -> None:
        wm = self.wave_mgr
        if wm.state == "prep":
            wm.prep_timer_ms -= dt_ms
            if wm.prep_timer_ms <= 0.0:
                self._call_wave_now()
        elif wm.state == "spawning":
            wm.spawn_timer_ms -= dt_ms
            if wm.spawn_timer_ms <= 0.0 and wm.spawn_queue:
                item = wm.spawn_queue.pop(0)
                self._spawn_enemy(item["type"])
                if wm.spawn_queue:
                    wm.spawn_timer_ms = float(wm.spawn_queue[0]["interval_ms"])
                else:
                    wm.state = "combat"
        elif wm.state == "combat":
            if not any(e.alive for e in self.enemies):
                # Wave Cleared!
                cfg = wm.get_wave_config(wm.current_wave)
                bonus = int(cfg.get("clear_bonus", 40))
                self.coins += bonus
                self.score += bonus * 3
                self._record_high_score()
                self.ev_manager.post(Event(EVENT_WAVE_CLEARED, data={"wave": wm.current_wave}))

                if wm.current_wave == wm.max_campaign_waves and not self.endless_mode:
                    self.ev_manager.post(Event(EVENT_VICTORY))
                    self.change_state("victory")
                    return

                wm.state = "prep"
                wm.prep_timer_ms = wm.prep_duration_ms
                self.banner_text = f"WAVE {wm.current_wave} CLEARED! (+{bonus} Gold)"
                self.banner_timer_ms = 2400.0

    def _spawn_enemy(self, enemy_type: str) -> None:
        diff_key = self.settings.get("difficulty", "normal")
        prof = DIFFICULTY_PROFILES.get(diff_key, DIFFICULTY_PROFILES["normal"])
        wave_scale = 1.0 + max(0, self.wave_mgr.current_wave - 1) * 0.12
        e = Enemy(
            enemy_type=enemy_type,
            road=self.road,
            hp_mult=prof["enemy_hp_mult"] * wave_scale,
            speed_mult=prof["enemy_speed_mult"] * self.ui_scale,
            gold_mult=prof["gold_reward_mult"],
        )
        self.enemies.append(e)
        self.ev_manager.post(Event(EVENT_ENEMY_SPAWNED, data={"type": enemy_type, "boss": e.boss}))

    def _update_meteors(self, dt_ms: float) -> None:
        for m in list(self.falling_meteors):
            if m["delay_ms"] > 0:
                m["delay_ms"] -= dt_ms
                continue
            m["progress"] += (dt_ms / 1000.0) * 2.2
            p = min(1.0, m["progress"])
            cx = m["x"] + (m["tx"] - m["x"]) * p
            cy = m["y"] + (m["ty"] - m["y"]) * p
            self.particles.spawn_hit((cx, cy), pal.FIRE_MID, count=2)
            if p >= 1.0:
                self.falling_meteors.remove(m)
                tx, ty = m["tx"], m["ty"]
                rad = m["radius"]
                self.particles.spawn_explosion((tx, ty), rad)
                self.trigger_shake(5.5, 250.0)
                for e in list(self.enemies):
                    if e.alive and math.hypot(e.x - tx, e.y - ty) <= rad:
                        dmg = e.take_damage(m["damage"], "explosive")
                        e.apply_burn(18.0, 3000.0)
                        self.on_enemy_damaged(e, dmg, is_crit=True, color=pal.FIRE_LIGHT)

    def _update_projectiles(self, dt_ms: float) -> None:
        dt_s = dt_ms / 1000.0
        for proj in list(self.projectiles):
            if not proj.active:
                self.projectiles.remove(proj)
                continue

            if proj.target is not None and proj.target.alive:
                proj.target_x, proj.target_y = proj.target.x, proj.target.y

            if proj.kind == "bomb":
                proj.flight_elapsed += dt_s
                t = min(1.0, proj.flight_elapsed / max(0.05, proj.flight_duration))
                proj.x = proj.start_x + (proj.target_x - proj.start_x) * t
                proj.y = proj.start_y + (proj.target_y - proj.start_y) * t
                proj.z_height = 4.0 * 75.0 * self.ui_scale * t * (1.0 - t)
                if t >= 1.0:
                    self._detonate_projectile(proj)
            else:
                dx = proj.target_x - proj.x
                dy = proj.target_y - proj.y
                dist = math.hypot(dx, dy)
                step = proj.speed * dt_s
                if dist <= max(14.0 * self.ui_scale, step):
                    proj.x, proj.y = proj.target_x, proj.target_y
                    self._detonate_projectile(proj)
                else:
                    proj.x += (dx / dist) * step
                    proj.y += (dy / dist) * step
                    proj.angle_deg = math.degrees(math.atan2(dy, dx))

    def _detonate_projectile(self, proj: Projectile) -> None:
        if proj in self.projectiles:
            self.projectiles.remove(proj)

        px, py = proj.x, proj.y
        if proj.kind == "bomb":
            self.particles.spawn_explosion((px, py), proj.splash_radius)
            self.trigger_shake(3.2, 160.0)
            r2 = proj.splash_radius ** 2
            for e in list(self.enemies):
                if e.alive and ((e.x - px) ** 2 + (e.y - py) ** 2) <= r2:
                    dmg = e.take_damage(proj.damage, "explosive")
                    self.on_enemy_damaged(e, dmg, is_crit=False, color=pal.FIRE_LIGHT)
        elif proj.kind == "frost":
            self.particles.spawn_frost_nova((px, py), proj.splash_radius)
            r2 = max(24.0, proj.splash_radius) ** 2
            for e in list(self.enemies):
                if e.alive and ((e.x - px) ** 2 + (e.y - py) ** 2) <= r2:
                    e.apply_slow(proj.slow_factor, proj.slow_duration_ms)
                    dmg = e.take_damage(proj.damage, "magic")
                    self.on_enemy_damaged(e, dmg, is_crit=False, color=pal.FROST_LIGHT)
        else:
            tgt = proj.target
            if tgt is not None and tgt.alive:
                is_crit = random.random() < proj.crit_chance
                raw_dmg = proj.damage * (1.75 if is_crit else 1.0)
                dmg = tgt.take_damage(raw_dmg, proj.damage_type)
                self.particles.spawn_hit((px, py), pal.GOLD_SHINE if is_crit else pal.ARCHER_GREEN_LIGHT, count=6)
                self.on_enemy_damaged(tgt, dmg, is_crit=is_crit, color=pal.GOLD_SHINE if is_crit else pal.UI_TEXT_WHITE)

        self.proj_pool.release(proj)

    def on_enemy_damaged(
        self,
        enemy: Enemy,
        dmg: float,
        is_crit: bool = False,
        color: Tuple[int, int, int] = pal.UI_TEXT_WHITE,
    ) -> None:
        if is_crit:
            self.particles.add_floating_text(enemy.pos, f"CRIT! -{int(dmg)}", pal.GOLD_SHINE, big=True)
        if not enemy.alive and not enemy.reached_castle:
            self._handle_enemy_death(enemy)

    def _handle_enemy_death(self, enemy: Enemy) -> None:
        if enemy in self.enemies:
            self.enemies.remove(enemy)
        self.coins += enemy.reward
        pts = enemy.reward * (10 if enemy.boss else 5)
        self.score += pts
        self._record_high_score()
        self.particles.spawn_hit(enemy.pos, pal.GOLD_LIGHT if enemy.boss else pal.CRIMSON_LIGHT, count=14 if enemy.boss else 9)
        self.particles.add_floating_text(enemy.pos, f"+{enemy.reward}G", pal.GOLD_SHINE)
        if enemy.boss:
            self.trigger_shake(6.0, 350.0)
        self.ev_manager.post(
            Event(EVENT_ENEMY_KILLED, data={"reward": enemy.reward, "score": pts, "pos": enemy.pos})
        )

    def notify_tower_fire(self, tower_type: str, pos: Tuple[float, float]) -> None:
        self.ev_manager.post(Event(EVENT_TOWER_FIRE, data={"type": tower_type, "pos": pos}))

    def trigger_shake(self, strength: float, duration_ms: float) -> None:
        self.shake_strength = max(self.shake_strength, float(strength))
        self.shake_timer_ms = max(self.shake_timer_ms, float(duration_ms))

    def _update_camera_shake(self, dt_ms: float) -> None:
        if self.shake_timer_ms > 0.0:
            self.shake_timer_ms = max(0.0, self.shake_timer_ms - dt_ms)
            rx = int(random.uniform(-1.0, 1.0) * self.shake_strength)
            ry = int(random.uniform(-1.0, 1.0) * self.shake_strength)
            self.camera_offset = (rx, ry)
        else:
            self.shake_strength = 0.0
            self.camera_offset = (0, 0)

    def _record_high_score(self) -> None:
        changed = False
        if self.score > self.settings.get("high_score", 0):
            self.settings["high_score"] = self.score
            changed = True
        if self.wave_mgr.current_wave > self.settings.get("best_wave", 1):
            self.settings["best_wave"] = self.wave_mgr.current_wave
            changed = True
        if changed:
            self.persist_settings()

    # ------------------------------------------------------------------
    # RENDER PIPELINE
    # ------------------------------------------------------------------
    def draw(self) -> None:
        if self.state == "menu":
            self.menus.draw_main_menu(self.screen, self)
            return
        if self.state == "settings":
            self.menus.draw_settings_menu(self.screen, self)
            return

        ox, oy = self.camera_offset
        s = self.ui_scale

        # 1. Baked Pixel-Art Battleground
        if self.map_surface:
            self.screen.blit(self.map_surface, (ox, oy))
        else:
            self.screen.fill(pal.GRASS_BASE)

        # 2. Tactical Build Slots & Towers
        for sl in self.road.slots:
            sx, sy = sl.pos[0] + ox, sl.pos[1] + oy
            is_hov = sl == self.hovered_slot
            is_sel = self.radial_menu.active_slot == sl
            pad_srf = self.pixel_gen.get_slot_pad(hovered=is_hov, selected=is_sel)
            self.screen.blit(pad_srf, pad_srf.get_rect(center=(sx, sy + int(4 * s))))

            if sl.tower is not None:
                tw = sl.tower
                base_srf = self.pixel_gen.get_tower_base(tw.tower_type, tw.level)
                tur_srf = self.pixel_gen.get_tower_turret(
                    tw.tower_type,
                    tw.level,
                    tw.angle_deg,
                    tw.anim_step,
                )
                rec_x, rec_y = 0, 0
                if tw.recoil_ms > 0:
                    rad = math.radians(tw.angle_deg)
                    rec_dist = -4.0 * s * (tw.recoil_ms / 140.0)
                    rec_x = int(math.cos(rad) * rec_dist)
                    rec_y = int(math.sin(rad) * rec_dist)

                self.screen.blit(base_srf, base_srf.get_rect(center=(sx, sy)))
                self.screen.blit(
                    tur_srf,
                    tur_srf.get_rect(center=(sx + rec_x, sy - int(12 * s) + rec_y)),
                )

                # Level stars badge below tower
                for st_i in range(tw.level):
                    st_x = sx + int((st_i - (tw.level - 1) / 2.0) * 10 * s)
                    st_y = sy + int(24 * s)
                    pygame.draw.rect(self.screen, pal.OUTLINE_DARK, (st_x - 3, st_y - 3, 7, 7))
                    pygame.draw.rect(self.screen, pal.GOLD_SHINE, (st_x - 2, st_y - 2, 5, 5))

        # 3. Royal Castle at Right End of Path
        cx, cy = self.road.castle_pos[0] + ox, self.road.castle_pos[1] + oy
        castle_srf = self.pixel_gen.get_castle_sprite(self.castle_hp / max(1.0, self.castle_hp_max))
        self.screen.blit(castle_srf, castle_srf.get_rect(center=(cx, cy)))

        # 4. Enemies (depth-sorted by Y position)
        sorted_enemies = sorted(self.enemies, key=lambda e: e.y)
        for e in sorted_enemies:
            if not e.alive:
                continue
            ex, ey = int(e.x + ox), int(e.y + oy)
            sh_w = int((36 if e.boss else 20) * s)
            sh_h = int((14 if e.boss else 8) * s)
            sh = pygame.Surface((sh_w, sh_h), pygame.SRCALPHA)
            pygame.draw.ellipse(sh, pal.SHADOW_ALPHA, (0, 0, sh_w, sh_h))
            self.screen.blit(sh, (ex - sh_w // 2, ey + int(10 * s)))

            spr = self.pixel_gen.get_enemy_sprite(
                e.enemy_type,
                walk_frame=e.walk_frame,
                hit_flash=(e.hit_flash_ms > 0),
                slowed=(e.slow_timer_ms > 0),
                facing_left=e.facing_left,
            )
            self.screen.blit(spr, spr.get_rect(center=(ex, ey - int(6 * s))))

            # Overhead Pixel HP Bar
            bw = int((46 if e.boss else 28) * s)
            bh = int((7 if e.boss else 5) * s)
            bx = ex - bw // 2
            by = ey - spr.get_height() // 2 - int(10 * s)
            pygame.draw.rect(self.screen, pal.OUTLINE_DARK, (bx - 1, by - 1, bw + 2, bh + 2))
            pygame.draw.rect(self.screen, (60, 20, 25), (bx, by, bw, bh))
            fill_w = int(bw * max(0.0, min(1.0, e.hp / max(1.0, e.hp_max))))
            bar_col = pal.UI_CYAN if e.slow_timer_ms > 0 else (pal.UI_RED if e.boss else pal.UI_GREEN)
            if fill_w > 0:
                pygame.draw.rect(self.screen, bar_col, (bx, by, fill_w, bh))

        # 5. Projectiles & Chain Lightning Arcs & Falling Meteors
        for proj in self.projectiles:
            if not proj.active:
                continue
            px, py = int(proj.x + ox), int(proj.y + oy)
            if proj.kind == "bomb" and proj.z_height > 0:
                pygame.draw.ellipse(
                    self.screen,
                    (15, 12, 22),
                    (px - int(8 * s), py - int(4 * s), int(16 * s), int(8 * s)),
                )
                py -= int(proj.z_height)
            psrf = self.pixel_gen.get_projectile_sprite(proj.kind, proj.angle_deg)
            self.screen.blit(psrf, psrf.get_rect(center=(px, py)))

        for arc in self.lightning_arcs:
            for seg in arc.segments:
                if len(seg) >= 2:
                    shifted = [(pt[0] + ox, pt[1] + oy) for pt in seg]
                    pygame.draw.lines(self.screen, pal.ARCANE_MID, False, shifted, 5)
                    pygame.draw.lines(self.screen, pal.ARCANE_CORE, False, shifted, 2)

        for m in self.falling_meteors:
            if m["delay_ms"] <= 0:
                p = min(1.0, m["progress"])
                mx_p = int(m["x"] + (m["tx"] - m["x"]) * p + ox)
                my_p = int(m["y"] + (m["ty"] - m["y"]) * p + oy)
                msrf = self.pixel_gen.get_projectile_sprite("meteor", 0.0)
                self.screen.blit(msrf, msrf.get_rect(center=(mx_p, my_p)))

        # 6. Particles & Floating Combat Text
        self.particles.draw(self.screen, self.camera_offset, self.font_small, self.font_mid)

        # 7. Wave / Spell Announcement Banner
        if self.banner_timer_ms > 0.0 and self.banner_text:
            draw_text_shadow(
                self.screen,
                self.font_big,
                self.banner_text,
                pal.GOLD_SHINE,
                pos=(self.width // 2, int(105 * s)),
                align="center",
            )

        # 8. Radial Menu & HUD & Overlays
        self.radial_menu.draw(self.screen, self)
        self.hud.draw(self.screen, self)
        self.menus.draw_overlay(self.screen, self)

    def run(self) -> None:
        while self.running:
            raw_dt = float(self.clock.tick(FPS))
            self.handle_events()
            self.update(raw_dt)
            self.draw()
            pygame.display.flip()


def main() -> None:
    init_logging()
    logger = get_logger(__name__)
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    cfg = load_settings(base_dir)
    ev_manager = EventManager()
    _sound_sys = SoundSystem(
        ev_manager,
        sfx_volume=float(cfg.get("sfx_volume", 0.7)),
        music_volume=float(cfg.get("music_volume", 0.5)),
    )
    game = TowerDefenseGame(ev_manager)
    logger.info("Tower Defense II started successfully.")
    game.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
