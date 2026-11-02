import pygame
import sys
import math
import os
from core.events import Event, EventManager, EVENT_ENEMY_KILLED, EVENT_TOWER_UPGRADED, EVENT_COINS_UPDATED, EVENT_TOGGLE_UPGRADE_PANEL, EVENT_MOUSE_CLICK, EVENT_TOGGLE_PAUSE, EVENT_GAME_OVER, EVENT_QUIT, EVENT_MANUAL_FIRE, EVENT_ULTI_USED, EVENT_TOGGLE_UPGRADE_DEBUG, EVENT_UPGRADE_DEBUG_ADJUST, EVENT_UPGRADE_DEBUG_SAVE, EVENT_UPGRADE_DEBUG_SELECT_TYPE, EVENT_UPGRADE_DEBUG_TOGGLE_LIMITS, EVENT_TOGGLE_MENU_DEBUG, EVENT_TOGGLE_SETTINGS_DEBUG, EVENT_TOGGLE_GO_DEBUG, EVENT_TOGGLE_PAUSED_DEBUG, EVENT_TOGGLE_DEBUG_RESIZE_MODE, EVENT_TOGGLE_HUD_DEBUG
from core.logger import init_logging, get_logger
from core.config import load_settings

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
    UPGRADE_COSTS = {'range': 80, 'firerate': 80, 'bullet': 80, 'sword': 80, 'bullet_power': 80, 'bullet_speed': 80}
    RANGE_UP_AMOUNT = 20
    FIRERATE_DELTA = 50
    BULLET_SPEED_DELTA = 30
    BULLET_DAMAGE_DELTA = 1
    SWORD_DAMAGE_BASE = 0.5
    SWORD_DAMAGE_DELTA = 0.75
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
            
        # Safe UI font for complex text (Upgrade panel etc.)
        self.ui_font = pygame.font.SysFont("arial", 20, bold=True)
        self.ui_font_small = pygame.font.SysFont("arial", 14)
            
        self.ENEMY_SPEED_TABLE = ENEMY_SPEED_TABLE
        self.UPGRADE_COSTS = UPGRADE_COSTS
        self.RANGE_UP_AMOUNT = RANGE_UP_AMOUNT
        self.FIRERATE_DELTA = FIRERATE_DELTA
        self.BULLET_SPEED_DELTA = BULLET_SPEED_DELTA
        self.BULLET_DAMAGE_DELTA = BULLET_DAMAGE_DELTA
        self.SWORD_DAMAGE_BASE = SWORD_DAMAGE_BASE
        self.SWORD_DAMAGE_DELTA = SWORD_DAMAGE_DELTA
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
        from gameplay.strategy import NearestTarget
        self.target_strategy = NearestTarget()
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
            'start': (0.521, 0.43900000000000006),
            'settings': (0.521, 0.568),
            'exit': (0.5180000000000001, 0.678),
        }
        self.go_restart_pos = (0.50, 0.62)
        self.go_exit_pos = (0.50, 0.72)
        self.settings_menu_img = None
        self.game_over_img = None
        self.exit_menu_img = None
        self.options_menu_img = None
        self.volume_up_img = None
        
        self.options_menu_base_size = None
        self.enemy_walk_frames = []
        self.enemy_attack_frames = []
        self.coin_effects = []
        self.kill_shockwaves = []
        self.upgrade_open = False
        self.upgrade_debug = False
        self.upgrade_debug_target = 'bars'
        self.upgrade_debug_selected_type = 'sword'
        self.upgrade_debug_loosen = False
        self.menu_debug = False
        self.menu_debug_selected = 'start'
        self.settings_debug = False
        self.settings_btn_pos = {
            'fs_toggle': (0.5075, 0.36933333333333335),
            'sound_toggle': (0.50625, 0.5093333333333333),
            'back': (0.51225, 0.6556666666666666),
            'vol_up': (0.613, 0.4806666666666667),
            'vol_down': (0.61, 0.5413333333333333),
            'music_slider': (0.50625, 0.62),
        }
        self.settings_debug_selected = 'fs_toggle'
        self.go_debug = False
        self.go_debug_selected = 'restart'
        self.paused_debug = False
        self.paused_btn_pos = {'continue': (0.5, 0.39899999999999997), 'settings': (0.503, 0.478), 'exit': (0.503, 0.5579999999999999), 'quit': (0.503, 0.641)}
        self.paused_btn_scale = {'continue': (0.838, 1.0), 'settings': (0.8140000000000001, 1.213), 'exit': (0.835, 1.222), 'quit': (0.811, 1.2369999999999994)}
        self.menu_btn_scale = {'start': (0.632, 0.5679999999999996), 'settings': (0.608, 0.649), 'exit': (0.584, 0.6159999999999999)}
        self.settings_btn_scale = {'fs_toggle': (1.0, 1.0), 'sound_toggle': (1.0, 0.9009999999999998), 'back': (0.994, 0.8469999999999995), 'vol_up': (0.664, 0.9129999999999993), 'vol_down': (0.7570000000000001, 0.988), 'music_slider': (1.0, 1.0), 'music_knob': (1.0, 1.0)}
        self.paused_debug_selected = 'continue'
        self.debug_resize_mode = False
        self.hud_debug = False
        self.hud_debug_selected = 'healthbar'
        self.hud_pos = {'healthbar': (0.10999999999999999, 0.07299999999999998), 'coinbar': (0.29, 0.06399999999999997), 'enemies': (0.6560000000000001, 0.06099999999999997), 'ulti': (0.11599999999999955, 0.1879999999999993), 'wave': (0.504, 0.06999999999999998)}
        self.hud_scale = {'healthbar': (1.0, 1.0), 'coinbar': (0.655, 0.673), 'enemies': (0.932, 1.2160000000000002), 'ulti': (1.105, 1.5460000000000003), 'wave': (1.0, 1.0)}
        self.upgrade_card_centers_pct = [0.238, 0.492, 0.747, 0.875]
        self.upgrade_card_center_y_pct = 0.445
        self.upgrade_card_w_pct = 0.19
        self.upgrade_card_h_pct = 0.58
        self.upgrade_card_center_x_offsets_pct = {'sword': 0.0, 'range': -0.06, 'bullet_power': -0.1250000000000003, 'bullet_speed': -0.06000000000000001}
        self.upgrade_card_center_y_offsets_pct = {'sword': 0.0, 'range': -0.04500000000000001, 'bullet_power': -0.042, 'bullet_speed': -0.054000000000000006}
        self.upgrade_container_w_ratio = 0.5
        self.upgrade_slot_gap_ratio = 0.006
        self.upgrade_bar_y_ratio = 0.11
        self.upgrade_container_w_ratio_by_type = {'sword': 0.4099999999999999, 'range': 0.4639999999999997, 'bullet_power': 0.4009999999999999, 'bullet_speed': 0.40700000000000003}
        self.upgrade_bar_y_ratio_by_type = {'sword': 0.20900000000000007, 'range': 0.11, 'bullet_power': 0.116, 'bullet_speed': 0.11}
        self.upgrade_plus_px = {'sword': (308,392,56,56), 'range': (617,392,56,56), 'bullet_power': (926,392,56,56), 'bullet_speed': (1235,392,56,56)}
        self.upgrade_plus_offsets_pct_by_type = {'sword': (-0.018, -0.036), 'range': (-0.069, -0.036000000000000004), 'bullet_power': (-0.11699999999999999, -0.039), 'bullet_speed': (-0.16500000000000004, -0.036000000000000004)}
        self.tower_hp_max = 90
        self.tower_hp = self.tower_hp_max
        self.sound_volume = 1.0
        self.music_volume = 0.5
        self.particles = []
        self.wave_index = 1
        self.wave_duration_ms = 30000
        self.wave_elapsed_ms = 0
        self.wave_enemy_base = 10
        self.wave_enemy_increment = 2
        self.wave_enemies_target = self.wave_enemy_base + (self.wave_index - 1) * self.wave_enemy_increment
        self.wave_enemies_spawned = 0
        self.wave_in_boss_phase = False
        self.wave_banner_ms = 0
        from engine.pool import BulletPool
        self.bullet_pool = BulletPool()
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
        self.hit_overlay_ms = 0
        self.tower_fallen_frames = []
        self.tower_fall_anim_index = 0
        self.tower_fall_anim_timer = 0
        self.tower_fall_active = False
        self.tower_damaged_imgs = []
        self.ulti_charge = 0
        self.ulti_max = 10
        self.sword_level = 0
        self.sword_damage = 0.0
        self.upgrade_levels = {
            'range': 0,
            'firerate': 0,
            'bullet': 0,
            'sword': 0,
            'bullet_power': 0,
            'bullet_speed': 0
        }
        self.upgrade_limits = {
            'range': 6,
            'firerate': 5,
            'bullet': 5,
            'sword': 5,
            'bullet_power': 5,
            'bullet_speed': 5
        }
        if not self.towers:
            from engine.factory import create_tower
            self.towers.append(create_tower((self.width - self.cell * 2, self.path_y - 80), range_px=300, fire_rate_ms=300))
        try:
            from assets.loader import load_images as _load_images, load_enemy_frames as _load_enemy_frames
            _load_images(self)
            _load_enemy_frames(self)
        except Exception as e:
            logger = get_logger(__name__)
            logger.error("Assets load error: %s", e)
            self.map_img = None
        cfg = load_settings(getattr(sys, '_MEIPASS', os.path.dirname(__file__)))
        self.sound_volume = float(cfg.get('sfx_volume', self.sound_volume))
        self.music_volume = float(cfg.get('music_volume', self.music_volume))
        self.fullscreen = bool(cfg.get('fullscreen', self.fullscreen))
        self.apply_display_mode()

    def notify(self, event):
        if event.name == EVENT_QUIT:
            self.running = False
        
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
            if self.ulti_charge < self.ulti_max:
                self.ulti_charge += 1
        elif event.name == EVENT_MANUAL_FIRE:
            self.manual_fire()
        elif event.name == EVENT_ULTI_USED:
            self.trigger_ulti()
        elif event.name == EVENT_COINS_UPDATED:
            prev = self.coins
            self.coins = event.data.get('coins', self.coins)
            if self.coins > prev:
                self.spawn_coin_ui_particles()
        elif event.name == EVENT_TOWER_UPGRADED:
            self.apply_upgrade(event.data.get('type'))
        elif event.name == EVENT_TOGGLE_UPGRADE_DEBUG:
            self.upgrade_debug = not getattr(self, 'upgrade_debug', False)
        elif event.name == EVENT_UPGRADE_DEBUG_TOGGLE_LIMITS:
            self.upgrade_debug_loosen = not getattr(self, 'upgrade_debug_loosen', False)
        elif event.name == EVENT_TOGGLE_MENU_DEBUG:
            self.menu_debug = not getattr(self, 'menu_debug', False)
        elif event.name == EVENT_TOGGLE_SETTINGS_DEBUG:
            self.settings_debug = not getattr(self, 'settings_debug', False)
        elif event.name == EVENT_TOGGLE_GO_DEBUG:
            self.go_debug = not getattr(self, 'go_debug', False)
        elif event.name == EVENT_TOGGLE_PAUSED_DEBUG:
            self.paused_debug = not getattr(self, 'paused_debug', False)
        elif event.name == EVENT_TOGGLE_HUD_DEBUG:
            self.hud_debug = not getattr(self, 'hud_debug', False)
        elif event.name == EVENT_TOGGLE_DEBUG_RESIZE_MODE:
            self.debug_resize_mode = not getattr(self, 'debug_resize_mode', False)
        elif event.name == EVENT_UPGRADE_DEBUG_SELECT_TYPE:
            d = event.data or {}
            if self.upgrade_debug:
                cur = getattr(self, 'upgrade_debug_selected_type', 'sword')
                order = ['sword','range','bullet_power','bullet_speed']
                if d.get('dir') in ('next','prev'):
                    i = order.index(cur); i = (i + (1 if d['dir']=='next' else -1)) % len(order)
                    self.upgrade_debug_selected_type = order[i]
                elif 'type' in d and d['type'] in order:
                    self.upgrade_debug_selected_type = d['type']
            elif self.menu_debug:
                cur = getattr(self, 'menu_debug_selected', 'start')
                order = ['start','settings','exit']
                if d.get('dir') in ('next','prev'):
                    i = order.index(cur); i = (i + (1 if d['dir']=='next' else -1)) % len(order)
                    self.menu_debug_selected = order[i]
                elif 'type' in d and d['type'] in order:
                    self.menu_debug_selected = d['type']
            elif self.settings_debug:
                cur = getattr(self, 'settings_debug_selected', 'fs_toggle')
                order = ['fs_toggle','sound_toggle','back','vol_up','vol_down']
                if d.get('dir') in ('next','prev'):
                    i = order.index(cur); i = (i + (1 if d['dir']=='next' else -1)) % len(order)
                    self.settings_debug_selected = order[i]
                elif 'type' in d and d['type'] in order:
                    self.settings_debug_selected = d['type']
            elif self.go_debug:
                cur = getattr(self, 'go_debug_selected', 'restart')
                order = ['restart','exit']
                if d.get('dir') in ('next','prev'):
                    i = order.index(cur); i = (i + (1 if d['dir']=='next' else -1)) % len(order)
                    self.go_debug_selected = order[i]
                elif 'type' in d and d['type'] in order:
                    self.go_debug_selected = d['type']
            elif self.paused_debug:
                cur = getattr(self, 'paused_debug_selected', 'continue')
                order = ['continue','settings','exit','quit']
                if d.get('dir') in ('next','prev'):
                    i = order.index(cur); i = (i + (1 if d['dir']=='next' else -1)) % len(order)
                    self.paused_debug_selected = order[i]
                elif 'type' in d and d['type'] in order:
                    self.paused_debug_selected = d['type']
            elif self.hud_debug:
                cur = getattr(self, 'hud_debug_selected', 'healthbar')
                order = ['healthbar','coinbar','enemies','ulti','wave']
                if d.get('dir') in ('next','prev'):
                    i = order.index(cur); i = (i + (1 if d['dir']=='next' else -1)) % len(order)
                    self.hud_debug_selected = order[i]
                elif 'type' in d and d['type'] in order:
                    self.hud_debug_selected = d['type']
        elif event.name == EVENT_UPGRADE_DEBUG_ADJUST:
            d = event.data or {}
            if d.get('field') == 'cycle':
                modes = ['cards','bars','plus']
                cur = getattr(self, 'upgrade_debug_target', 'bars')
                idx = (modes.index(cur) + 1) % len(modes)
                self.upgrade_debug_target = modes[idx]
            else:
                delta = float(d.get('delta', 0.0))
                axis = d.get('axis')
                loosen = getattr(self, 'upgrade_debug_loosen', False)
                if self.upgrade_debug:
                    tgt = getattr(self, 'upgrade_debug_target', 'bars')
                    typ = getattr(self, 'upgrade_debug_selected_type', 'sword')
                    if tgt == 'cards':
                        xlim = 0.40 if loosen else 0.20; ylim = 0.40 if loosen else 0.20
                        if axis == 'x':
                            self.upgrade_card_center_x_offsets_pct[typ] = max(-xlim, min(xlim, self.upgrade_card_center_x_offsets_pct[typ] + delta))
                        else:
                            self.upgrade_card_center_y_offsets_pct[typ] = max(-ylim, min(ylim, self.upgrade_card_center_y_offsets_pct[typ] + delta))
                    elif tgt == 'bars':
                        low = 0.05 if loosen else 0.15; high = 0.95 if loosen else 0.90
                        if axis == 'x':
                            self.upgrade_container_w_ratio_by_type[typ] = max(low, min(high, self.upgrade_container_w_ratio_by_type[typ] + delta))
                        else:
                            ylow = 0.02 if loosen else 0.04; yhigh = 0.35 if loosen else 0.28
                            self.upgrade_bar_y_ratio_by_type[typ] = max(ylow, min(yhigh, self.upgrade_bar_y_ratio_by_type[typ] + delta))
                    else:
                        dlim = 0.20 if loosen else 0.12
                        dx, dy = self.upgrade_plus_offsets_pct_by_type[typ]
                        if axis == 'x': dx = max(-dlim, min(dlim, dx + delta))
                        else: dy = max(-dlim, min(dlim, dy + delta))
                        self.upgrade_plus_offsets_pct_by_type[typ] = (dx, dy)
                elif self.menu_debug:
                    key = getattr(self, 'menu_debug_selected', 'start')
                    if getattr(self, 'debug_resize_mode', False):
                        sx, sy = self.menu_btn_scale[key]
                        lim = (0.2, 4.0) if loosen else (0.5, 2.5)
                        if axis == 'x': sx = max(lim[0], min(lim[1], sx + delta))
                        else: sy = max(lim[0], min(lim[1], sy + delta))
                        self.menu_btn_scale[key] = (sx, sy)
                    else:
                        x, y = self.menu_btn_pos[key]
                        xlim = (-0.2, 1.2) if loosen else (0.0, 1.0)
                        ylim = (-0.2, 1.2) if loosen else (0.0, 1.0)
                        if axis == 'x': x = max(xlim[0], min(xlim[1], x + delta))
                        else: y = max(ylim[0], min(ylim[1], y + delta))
                        self.menu_btn_pos[key] = (x, y)
                elif self.settings_debug:
                    key = getattr(self, 'settings_debug_selected', 'fs_toggle')
                    if getattr(self, 'debug_resize_mode', False):
                        sx, sy = self.settings_btn_scale[key]
                        lim = (0.2, 4.0) if loosen else (0.5, 2.5)
                        if axis == 'x': sx = max(lim[0], min(lim[1], sx + delta))
                        else: sy = max(lim[0], min(lim[1], sy + delta))
                        self.settings_btn_scale[key] = (sx, sy)
                    else:
                        x, y = self.settings_btn_pos[key]
                        xlim = (-0.2, 1.2) if loosen else (0.0, 1.0)
                        ylim = (-0.2, 1.2) if loosen else (0.0, 1.0)
                        if axis == 'x': x = max(xlim[0], min(xlim[1], x + delta))
                        else: y = max(ylim[0], min(ylim[1], y + delta))
                        self.settings_btn_pos[key] = (x, y)
                elif self.go_debug:
                    key = getattr(self, 'go_debug_selected', 'restart')
                    if getattr(self, 'debug_resize_mode', False):
                        pair = {'restart': 'restart_btn_rect', 'exit': 'go_exit_btn_rect'}[key]
                        rect = getattr(self, pair)
                        lim = (0.2, 4.0) if loosen else (0.5, 2.5)
                        if axis == 'x': rect.width = max(8, int(rect.width * (1.0 + delta)))
                        else: rect.height = max(8, int(rect.height * (1.0 + delta)))
                    else:
                        pair = {'restart': 'go_restart_pos', 'exit': 'go_exit_pos'}[key]
                        x, y = getattr(self, pair)
                        xlim = (-0.2, 1.2) if loosen else (0.0, 1.0)
                        ylim = (-0.2, 1.2) if loosen else (0.0, 1.0)
                        if axis == 'x': x = max(xlim[0], min(xlim[1], x + delta))
                        else: y = max(ylim[0], min(ylim[1], y + delta))
                        setattr(self, pair, (x, y))
                elif self.paused_debug:
                    key = getattr(self, 'paused_debug_selected', 'continue')
                    if getattr(self, 'debug_resize_mode', False):
                        sx, sy = self.paused_btn_scale[key]
                        lim = (0.2, 4.0) if loosen else (0.5, 2.5)
                        if axis == 'x': sx = max(lim[0], min(lim[1], sx + delta))
                        else: sy = max(lim[0], min(lim[1], sy + delta))
                        self.paused_btn_scale[key] = (sx, sy)
                    else:
                        x, y = self.paused_btn_pos[key]
                        xlim = (-0.2, 1.2) if loosen else (0.0, 1.0)
                        ylim = (-0.2, 1.2) if loosen else (0.0, 1.0)
                        if axis == 'x': x = max(xlim[0], min(xlim[1], x + delta))
                        else: y = max(ylim[0], min(ylim[1], y + delta))
                        self.paused_btn_pos[key] = (x, y)
                elif self.hud_debug:
                    key = getattr(self, 'hud_debug_selected', 'healthbar')
                    if getattr(self, 'debug_resize_mode', False):
                        sx, sy = self.hud_scale[key]
                        lim = (0.2, 4.0) if loosen else (0.5, 2.5)
                        if axis == 'x': sx = max(lim[0], min(lim[1], sx + delta))
                        else: sy = max(lim[0], min(lim[1], sy + delta))
                        self.hud_scale[key] = (sx, sy)
                    else:
                        x, y = self.hud_pos[key]
                        xlim = (-0.2, 1.2) if loosen else (0.0, 1.0)
                        ylim = (-0.2, 1.2) if loosen else (0.0, 1.0)
                        if axis == 'x': x = max(xlim[0], min(xlim[1], x + delta))
                        else: y = max(ylim[0], min(ylim[1], y + delta))
                        self.hud_pos[key] = (x, y)
        elif event.name == EVENT_UPGRADE_DEBUG_SAVE:
            print("[Anchors] Copy-paste into GameEngine.__init__:")
            if self.upgrade_debug:
                print(f"self.upgrade_card_centers_pct = {self.upgrade_card_centers_pct}")
                print(f"self.upgrade_card_center_y_pct = {self.upgrade_card_center_y_pct}")
                print(f"self.upgrade_card_w_pct = {self.upgrade_card_w_pct}")
                print(f"self.upgrade_card_h_pct = {self.upgrade_card_h_pct}")
                print(f"self.upgrade_card_center_x_offsets_pct = {self.upgrade_card_center_x_offsets_pct}")
                print(f"self.upgrade_card_center_y_offsets_pct = {self.upgrade_card_center_y_offsets_pct}")
                print(f"self.upgrade_container_w_ratio = {self.upgrade_container_w_ratio}")
                print(f"self.upgrade_slot_gap_ratio = {self.upgrade_slot_gap_ratio}")
                print(f"self.upgrade_bar_y_ratio = {self.upgrade_bar_y_ratio}")
                print(f"self.upgrade_container_w_ratio_by_type = {self.upgrade_container_w_ratio_by_type}")
                print(f"self.upgrade_bar_y_ratio_by_type = {self.upgrade_bar_y_ratio_by_type}")
                print(f"self.upgrade_plus_offsets_pct_by_type = {self.upgrade_plus_offsets_pct_by_type}")
            elif self.menu_debug:
                print(f"self.menu_btn_pos = {self.menu_btn_pos}")
                print(f"self.menu_btn_scale = {self.menu_btn_scale}")
            elif self.settings_debug:
                print(f"self.settings_btn_pos = {self.settings_btn_pos}")
                print(f"self.settings_btn_scale = {self.settings_btn_scale}")
            elif self.go_debug:
                print(f"self.go_restart_pos = {self.go_restart_pos}")
                print(f"self.go_exit_pos = {self.go_exit_pos}")
                print("GameOver button sizes are adjusted live; persist by setting paused_btn_scale or adjusting draw code similarly.")
            elif self.paused_debug:
                print(f"self.paused_btn_pos = {self.paused_btn_pos}")
                print(f"self.paused_btn_scale = {self.paused_btn_scale}")
            elif self.hud_debug:
                print(f"self.hud_pos = {self.hud_pos}")
                print(f"self.hud_scale = {self.hud_scale}")
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
            # First, allow clicking ULTI bar to trigger ulti when ready
            try:
                s = getattr(self, 'ui_scale', 1.0)
                hp = getattr(self, 'hud_pos', {'ulti': (0.12, 0.20)})
                hs = getattr(self, 'hud_scale', {'ulti': (1.0, 1.0)})
                bw, bh = int(self.BASE_HUD_SIZE[0] * s), int(self.BASE_HUD_SIZE[1] * s)
                ur_w = max(8, int(bw * hs['ulti'][0]))
                ur_h = max(8, int(int(20 * s) * hs['ulti'][1]))
                ur_rect = pygame.Rect(0, 0, ur_w, ur_h)
                ur_rect.center = (int(self.width * hp['ulti'][0]), int(self.height * hp['ulti'][1]))
                if ur_rect.collidepoint(pos) and self.ulti_charge >= self.ulti_max:
                    try:
                        self.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'hud:ulti'}))
                    except Exception:
                        pass
                    self.trigger_ulti()
                    return
            except Exception:
                pass
            # Otherwise, normal tower selection
            from gameplay.towers import select_tower as _sel
            _sel(self, pos)

    def _handle_enemy_killed(self, data):
        if self.coin_img and data and 'pos' in data:
            px, py = data['pos']
            coins = data.get('coins', 5)
            self.coin_effects.append({'pos': [float(px), float(py)], 'ttl': COIN_EFFECT_TTL_MS, 'amount': coins})
            self.spawn_hit_particles((px, py), count=12)
            self.trigger_shake(strength=3.0, duration_ms=200)
            self.kill_shockwaves.append({'pos': [float(px), float(py)], 'ttl': 420})




    def manual_fire(self):
        from gameplay.towers import manual_fire as _mf
        _mf(self)

    def trigger_ulti(self):
        if self.ulti_charge < self.ulti_max:
            return
        self.ulti_charge = 0
        self.trigger_shake(strength=5.0, duration_ms=400)
        
        # Center of repulsion (use first tower if available, else center)
        if self.towers:
            center_x, center_y = self.towers[0]['pos']
            # Adjust for center of tower image
            center_x += self.cell
            center_y += self.cell
        else:
            center_x, center_y = self.width // 2, self.height // 2
            
        for enemy in self.enemies:
            dx = enemy['pos'][0] - center_x
            dy = enemy['pos'][1] - center_y
            dist = math.hypot(dx, dy)
            if dist > 0:
                # Normalize direction
                nx, ny = dx / dist, dy / dist
                # Knockback speed (pixels per second)
                kb_speed = 600.0
                enemy['knockback'] = {
                    'vel': (nx * kb_speed, ny * kb_speed),
                    'timer': 500 # 0.5 seconds
                }
                
        # Visual effect
        self.kill_shockwaves.append({'pos': [float(center_x), float(center_y)], 'ttl': 800})
        
        # Wind particles (expanding ring)
        for i in range(36):
            angle = math.radians(i * 10)
            speed = 400.0 # Initial outward speed
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append({
                'pos': [float(center_x), float(center_y)],
                'vel': [vx, vy],
                'ttl': 600,
                'kind': 'wind', # New particle type
                'color': (200, 255, 255, 150)
            })


    def apply_upgrade(self, up_type):
        from engine.upgrades import apply_upgrade as _au
        _au(self, up_type)

    

    def update(self, dt_ms):
        if self.state == 'paused':
            self.update_rain(dt_ms)
            return
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
        if getattr(self, 'wave_banner_ms', 0) > 0:
            self.wave_banner_ms = max(0, self.wave_banner_ms - dt_ms)
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
        self.enemies.clear(); self.bullets.clear(); self.coin_effects.clear(); self.kill_shockwaves.clear()
        self.elapsed_ms = 0; self.spawn_ms = 0
        self.next_boss_ms = self.boss_interval_ms
        self.boss_alert_ms = 0; self.boss_banner_ms = 0
        # Reset waves
        self.wave_index = 1
        self.wave_elapsed_ms = 0
        self.wave_enemies_target = self.wave_enemy_base
        self.wave_enemies_spawned = 0
        self.wave_in_boss_phase = False
        self.wave_banner_ms = 0
        self.selected_tower_idx = None
        self.ulti_charge = 0
        self.tower_hp = self.tower_hp_max
        self.tower_fall_active = False
        self.tower_fall_anim_index = 0
        self.tower_fall_anim_timer = 0
        self.camera_offset = (0, 0)
        self.shake_strength = 0.0
        # Coins ve upgrade seviyeleri korunur; UI senkronizasyonu için mevcut coins'i yayınla
        self.ev_manager.post(Event(EVENT_COINS_UPDATED, data={'coins': self.coins}))
        # Kuleleri varsayılana döndür ve upgrade seviyelerine göre uygulama yap
        from engine.factory import create_tower
        base_tower = create_tower((self.width - self.cell * 2, self.path_y - 80), range_px=300, fire_rate_ms=300)
        r_lvl = int(self.upgrade_levels.get('range', 0))
        fr_lvl = int(self.upgrade_levels.get('firerate', 0))
        if r_lvl > 0:
            base_tower['range'] = int(base_tower['range'] * (2.0 ** r_lvl))
        if fr_lvl > 0:
            base_tower['fire_rate'] = max(100, base_tower['fire_rate'] - fr_lvl * self.FIRERATE_DELTA)
        self.towers = [base_tower]

# --- 4. ANA PROGRAM (MAIN) ---
def main():
    init_logging()
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
