import pygame
import sys
import math
import os
import random
from core.events import Event, EventManager, EVENT_ENEMY_KILLED, EVENT_TOWER_FIRE, EVENT_TOWER_PLACED, EVENT_PATH_SET, EVENT_UPGRADE_TOWER, EVENT_TOWER_UPGRADED, EVENT_COINS_UPDATED, EVENT_TOGGLE_UPGRADE_PANEL, EVENT_MOUSE_CLICK, EVENT_TOGGLE_PAUSE, EVENT_GAME_OVER, EVENT_QUIT, EVENT_SOUND_VOLUME_CHANGED, EVENT_BOSS_NEAR, EVENT_MANUAL_FIRE

# --- 1-2. OLAYLAR VE YÖNETİCİ ---

from systems.input import KeyboardController

from systems.sound import SoundSystem

from systems.score import ScoreSystem
try:
    from config import ENEMY_SPEED_TABLE, UPGRADE_COSTS, RANGE_UP_AMOUNT, FIRERATE_DELTA, BULLET_SPEED_DELTA, BULLET_DAMAGE_DELTA, COIN_EFFECT_TTL_MS, COIN_EFFECT_RISE_SPEED
except Exception:
    ENEMY_SPEED_TABLE = [
        (25000, 50.0),
        (50000, 60.0),
        (70000, 70.0),
        (100000, 80.0),
        (125000, 85.0),
        (float('inf'), 90.0),
    ]
    UPGRADE_COSTS = {'range': 80, 'firerate': 80, 'bullet': 80}
    RANGE_UP_AMOUNT = 20
    FIRERATE_DELTA = 50
    BULLET_SPEED_DELTA = 30
    BULLET_DAMAGE_DELTA = 1
    COIN_EFFECT_TTL_MS = 800
    COIN_EFFECT_RISE_SPEED = 0.05
    BASE_TOWER_SIZE = (220, 220)
    BASE_ENEMY_SIZE = (110, 110)
    BASE_BULLET_SIZE = (50, 50)
    BASE_PREV_SIZE = (36, 36)
    BASE_HUD_SIZE = (150, 75)

class GameEngine:
    """Oyunun ana döngüsünü ve çizimlerini yönetir."""
    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.register(self)
        self.running = True
        pygame.init()
        self.width, self.height = 800, 600
        self.base_width, self.base_height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Event Driven Tower Defense")
        self.clock = pygame.time.Clock()
        # Global UI font setup: use one TTF for all in-game text
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        icon_png = os.path.join(base_dir, 'assets', 'icon32.png')
        self.start_icon_img = None
        if os.path.exists(icon_png):
            try:
                _img = pygame.image.load(icon_png).convert_alpha()
                self.start_icon_img = _img
                pygame.display.set_icon(_img)
            except Exception:
                self.start_icon_img = None
        try:
            import pyi_splash
            pyi_splash.close()
        except Exception:
            pass
        ttf_path = os.path.join(base_dir, 'assets', 'counter.ttf')
        if os.path.exists(ttf_path):
            self.font = pygame.font.Font(ttf_path, 22)
            self.font_big = pygame.font.Font(ttf_path, 42)
            self.font_small = pygame.font.Font(ttf_path, 16)
            self.counter_font = pygame.font.Font(ttf_path, 40)
        else:
            self.font = pygame.font.SysFont(None, 22)
            self.font_big = pygame.font.SysFont(None, 42)
            self.font_small = pygame.font.SysFont(None, 16)
            self.counter_font = None
        self.ENEMY_SPEED_TABLE = ENEMY_SPEED_TABLE
        self.UPGRADE_COSTS = UPGRADE_COSTS
        self.RANGE_UP_AMOUNT = RANGE_UP_AMOUNT
        self.FIRERATE_DELTA = FIRERATE_DELTA
        self.BULLET_SPEED_DELTA = BULLET_SPEED_DELTA
        self.BULLET_DAMAGE_DELTA = BULLET_DAMAGE_DELTA
        self.COIN_EFFECT_TTL_MS = COIN_EFFECT_TTL_MS
        self.COIN_EFFECT_RISE_SPEED = COIN_EFFECT_RISE_SPEED
        self.BASE_TOWER_SIZE = BASE_TOWER_SIZE
        self.BASE_ENEMY_SIZE = BASE_ENEMY_SIZE
        self.BASE_BULLET_SIZE = BASE_BULLET_SIZE
        self.BASE_PREV_SIZE = BASE_PREV_SIZE
        self.BASE_HUD_SIZE = BASE_HUD_SIZE
        self.cell = 40
        self.ui_scale = 1.0
        self.intro_anim_active = True
        self.intro_anim_p = 0.0
        self.intro_anim_dur_ms = 1500.0
        self.intro_anim_start_ms = pygame.time.get_ticks()
        self.intro_anim_started = False
        self.path_y = self.height // 2
        self.towers = []
        self.enemies = []
        self.bullets = []
        self.spawn_ms = 0
        self.spawn_interval = 1800
        self.elapsed_ms = 0
        self.auto_fire = False
        self.coins = 0
        self.bullet_speed = 280.0
        self.bullet_damage = 1
        self.state = 'menu'
        self.fullscreen = False
        self.sound_enabled = True
        self.map_img = None
        self.tower_img = None
        self.enemy_img = None
        self.bullet_img = None
        self.coin_img = None
        self.healthbar_img = None
        self.healthbar_imgs = []
        self.coinbar_img = None
        self.upgrademenu_img = None
        self.upgrade_anim_offset = 0
        self.upgrade_anim_running = False
        self.transition_active = False
        self.transition_ms = 0
        self.transition_dur = 350
        self.transition_from = None
        self.transition_to = None
        self.transition_style = 'slide'
        self.transition_dir = 1
        self.previous_img = None
        self.enemies_counter_img = None
        self.main_menu_img = None
        self.playbutton_img = None
        self.setting_button_img = None
        self.menu_btn_pos = {
            'start': (0.50, 0.43),
            'settings': (0.50, 0.547),
            'exit': (0.50, 0.663),
        }
        self.go_restart_pos = (0.50, 0.62)
        self.go_exit_pos = (0.50, 0.72)
        self.settings_menu_img = None
        self.game_over_img = None
        self.exit_menu_img = None
        self.options_menu_img = None
        self.volume_up_img = None
        self.exit_menu_img = None
        self.options_menu_img = None
        self.options_menu_base_size = None
        self.enemy_walk_frames = []
        self.enemy_attack_frames = []
        self.coin_effects = []
        self.kill_shockwaves = []
        self.upgrade_open = False
        self.tower_hp_max = 90
        self.tower_hp = self.tower_hp_max
        self.sound_volume = 1.0
        self.particles = []
        self.camera_offset = (0, 0)
        self.shake_timer = 0
        self.shake_strength = 0.0
        self.shake_decay = 0.005
        self.rain_enabled = True
        self.rain_intensity = 0.7
        self.rain_wind = 0.3
        self.rain_drops = []
        self.last_dt_ms = 0
        self.boss_interval_ms = 60000
        self.next_boss_ms = self.boss_interval_ms
        self.boss_alert_ms = 0
        self.selected_tower_idx = None
        self.boss_banner_ms = 0
        self.boss_banner_ms = 0
        self.hit_overlay_ms = 0
        if not self.towers:
            self.towers.append({'pos': (self.width - self.cell * 2, self.path_y - 80), 'range': 200, 'cooldown': 0, 'fire_rate': 300})
        try:
            from assets.loader import load_images as _load_images, load_enemy_frames as _load_enemy_frames
            _load_images(self)
            _load_enemy_frames(self)
        except Exception as e:
            print(f"[Assets] Load error: {e}", file=sys.stderr)
            self.map_img = None
        self.apply_display_mode()

    def notify(self, event):
        if event.name == EVENT_QUIT:
            self.running = False
        elif event.name == EVENT_TOWER_PLACED:
            pass
        elif event.name == EVENT_PATH_SET:
            pass
        elif event.name == EVENT_TOGGLE_UPGRADE_PANEL:
            self.upgrade_open = not self.upgrade_open
        elif event.name == EVENT_TOGGLE_PAUSE:
            if self.state == 'playing':
                self.start_transition('paused', style='zoom')
            elif self.state == 'paused':
                self.start_transition('playing', style='zoom')
        elif event.name == EVENT_MOUSE_CLICK:
            self._handle_mouse_click(event.data['pos'])
        elif event.name == EVENT_ENEMY_KILLED:
            self._handle_enemy_killed(event.data)
        elif event.name == EVENT_MANUAL_FIRE:
            self.manual_fire()
        elif event.name == EVENT_COINS_UPDATED:
            prev = self.coins
            self.coins = event.data.get('coins', self.coins)
            if self.coins > prev:
                self.spawn_coin_ui_particles()
        elif event.name == EVENT_TOWER_UPGRADED:
            self.apply_upgrade(event.data.get('type'))
        elif event.name == EVENT_GAME_OVER:
            self.go_anim_p = 0.0
            self.go_anim_dur_ms = 850.0

    def _handle_mouse_click(self, pos):
        if self.state == 'menu':
            from ui.menu import handle_menu_click as _h
            _h(self, pos)
        elif self.state == 'settings':
            from ui.settings import handle_settings_click as _h
            _h(self, pos)
        elif self.state == 'paused':
            from ui.overlays import handle_paused_click as _h
            _h(self, pos)
        elif self.state == 'game_over':
            from ui.overlays import handle_game_over_click as _h
            _h(self, pos)
        elif self.upgrade_open:
            from ui.upgrade import handle_upgrade_click as _h
            _h(self, pos)
        elif self.state == 'playing':
            from gameplay.towers import select_tower as _sel
            _sel(self, pos)

    def _handle_enemy_killed(self, data):
        if self.coin_img and data and 'pos' in data:
            px, py = data['pos']
            self.coin_effects.append({'pos': [float(px), float(py)], 'ttl': COIN_EFFECT_TTL_MS})
            self.spawn_hit_particles((px, py), count=12)
            self.trigger_shake(strength=3.0, duration_ms=200)
            self.kill_shockwaves.append({'pos': [float(px), float(py)], 'ttl': 420})




    def manual_fire(self):
        from gameplay.towers import manual_fire as _mf
        _mf(self)

    def apply_upgrade(self, up_type):
        from engine.upgrades import apply_upgrade as _au
        _au(self, up_type)

    def enemy_speed_for_time(self, t_ms):
        from gameplay.enemies import enemy_speed_for_time as _es
        return _es(self, t_ms)

    def spawn_params_for_time(self, t_ms):
        from gameplay.enemies import spawn_params_for_time as _sp
        return _sp(self, t_ms)

    def update(self, dt_ms):
        if self.state != 'playing':
            return
        self.last_dt_ms = dt_ms
        if self.upgrade_open:
            return
        self.elapsed_ms += dt_ms
        self.update_spawn(dt_ms)
        from gameplay.enemies import update_enemies as _ue
        from gameplay.towers import update_towers as _ut
        from gameplay.bullets import update_bullets as _ub
        _ue(self, dt_ms)
        _ut(self, dt_ms)
        _ub(self, dt_ms)
        self.update_coin_effects(dt_ms)
        self.update_particles(dt_ms)
        self.update_rain(dt_ms)
        self.update_camera_shake(dt_ms)
        if self.boss_alert_ms > 0:
            self.boss_alert_ms = max(0, self.boss_alert_ms - dt_ms)
        if self.boss_banner_ms > 0:
            self.boss_banner_ms = max(0, self.boss_banner_ms - dt_ms)
        if getattr(self, 'hit_overlay_ms', 0) > 0:
            self.hit_overlay_ms = max(0, self.hit_overlay_ms - dt_ms)

    def update_spawn(self, dt_ms):
        from gameplay.enemies import update_spawn as _us
        _us(self, dt_ms)


    def update_particles(self, dt_ms):
        from engine.render import update_particles as _up
        _up(self, dt_ms)

    def update_rain(self, dt_ms):
        from engine.render import update_rain as _ur
        _ur(self, dt_ms)

    def update_camera_shake(self, dt_ms):
        from engine.render import update_camera_shake as _uc
        _uc(self, dt_ms)

    def trigger_shake(self, strength=2.0, duration_ms=150):
        from engine.render import trigger_shake as _ts
        _ts(self, strength, duration_ms)

    def spawn_hit_particles(self, pos, count=12):
        from engine.render import spawn_hit_particles as _sh
        _sh(self, pos, count)

    def spawn_muzzle_flash(self, pos, count=8):
        from engine.render import spawn_muzzle_flash as _sm
        _sm(self, pos, count)

    def spawn_upgrade_particles(self, pos, count=10):
        from engine.render import spawn_upgrade_particles as _su
        _su(self, pos, count)

    def spawn_coin_ui_particles(self, count=8):
        from engine.render import spawn_coin_ui_particles as _sc
        _sc(self, count)

    def update_coin_effects(self, dt_ms):
        from engine.render import update_coin_effects as _uce
        _uce(self, dt_ms)

    def find_target(self, tower):
        from gameplay.towers import find_target as _ft
        return _ft(self, tower)

    def draw_text_shadow(self, font, text, color, rect=None, align='center', pos=None):
        from ui.hud import _draw_text_shadow as _d
        return _d(self.screen, font, text, color, rect, align, pos)

    def draw(self):
        if getattr(self, 'transition_active', False):
            from engine.transitions import render_with_transition as _render
            _render(self)
            return
        self.draw_background()
        self.draw_towers()
        self.draw_enemies()
        self.draw_bullets()
        self.draw_rain()
        self.draw_ui()
        self.draw_overlays()
        if getattr(self, 'intro_anim_active', False):
            from ui.overlays import draw_intro as _intro
            _intro(self)

    def _render_scene_for_state(self, state, surface):
        from engine.transitions import render_scene_for_state as _render_scene
        _render_scene(self, state, surface)

    def draw_background(self):
        from engine.render import draw_background as _bg
        _bg(self)

    def draw_towers(self):
        from engine.render import draw_towers as _dt
        _dt(self)

    def draw_enemies(self):
        from engine.render import draw_enemies as _de
        _de(self)

    def draw_bullets(self):
        from engine.render import draw_bullets as _db
        _db(self)
        
    def draw_rain(self):
        from engine.render import draw_rain as _dr
        _dr(self)
        

    def draw_ui(self):
        from ui.hud import draw_ui as _draw_ui
        _draw_ui(self)

    def draw_overlays(self):
        from ui.overlays import draw_overlays as _draw_ov
        _draw_ov(self)

    def run(self, input_sys):
        while self.running:
            input_sys.check_inputs()
            dt = self.clock.tick(60)
            self.last_dt_ms = dt
            self.update(dt)
            self.draw()
            pygame.display.flip()

    def get_upgrade_buttons(self):
        from engine.upgrades import get_buttons as _gb
        return _gb(self)

    def draw_upgrade_panel(self):
        from ui.upgrade import draw_upgrade_panel as _up
        _up(self)
            

    def draw_menu(self):
        from ui.menu import draw_menu as _menu
        _menu(self)

    def start_transition(self, next_state, style='slide', dir=None):
        from engine.transitions import start_transition as _st
        _st(self, next_state, style, dir)

    def draw_settings(self):
        from ui.settings import draw_settings as _draw_settings
        _draw_settings(self)

    def apply_display_mode(self):
        from engine.render import apply_display_mode as _adm
        _adm(self)

    def reset_game(self):
        self.enemies.clear(); self.bullets.clear(); self.coin_effects.clear()
        self.elapsed_ms = 0; self.spawn_ms = 0
        self.tower_hp = self.tower_hp_max
        self.ev_manager.post(Event(EVENT_COINS_UPDATED, data={'coins': self.coins}))

# --- 4. ANA PROGRAM (MAIN) ---
def main():
    ev_manager = EventManager()
    input_sys = KeyboardController(ev_manager)
    sound_sys = SoundSystem(ev_manager)
    score_sys = ScoreSystem(ev_manager)
    game_engine = GameEngine(ev_manager)

    # Simülasyon: Diyelim ki oyun başladı ve bir düşman öldü
    # Bunu manuel tetikliyorum ki mantığı gör:
    game_engine.run(input_sys)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
