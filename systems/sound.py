import os
import sys
import pygame
from core.events import EVENT_TOWER_FIRE, EVENT_ENEMY_KILLED, EVENT_TOWER_PLACED, EVENT_SOUND_VOLUME_CHANGED, EVENT_BOSS_NEAR, EVENT_UI_HOVER, EVENT_SOUND_TOGGLE, EVENT_MOUSE_CLICK, EVENT_STATE_CHANGED, EVENT_TOWER_UPGRADED, EVENT_UI_CLICK, EVENT_ENEMY_SPAWNED

class SoundSystem:
    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.register(self)
        self.volume = 1.0
        self.enabled = True
        self.debug_sound_logs = False
        try:
            pygame.mixer.init()
        except Exception:
            pass
        self.tick = None
        self.rain_sound = None
        self.bullet_snd = None
        self.enemy_snd = None
        self.upgrade_snd = None
        self.rain_playing = False
        self._last_state = None
        base_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        def _pick_existing(paths):
            for p in paths:
                if os.path.exists(p):
                    return p
            return None
        tick_path = _pick_existing([
            os.path.join(base_dir, 'assets', 'tick.wav'),
            os.path.join(base_dir, 'assets', 'ui_tick.wav'),
            os.path.join(base_dir, 'assets', 'tick_effect.wav'),
            os.path.join(base_dir, 'assets', 'click.wav'),
            os.path.join(base_dir, 'assets', 'hover.wav'),
            os.path.join(base_dir, 'assets', 'hover_click.wav'),
        ])
        bg_path = os.path.join(base_dir, 'assets', 'background_effect.wav')
        war_path = os.path.join(base_dir, 'assets', 'war_effect.wav')
        self._bg_music_path = bg_path if os.path.exists(bg_path) else None
        self._war_music_path = war_path if os.path.exists(war_path) else None
        self._current_music_kind = None
        rain_path = os.path.join(base_dir, 'assets', 'rain.wav')
        upgrade_path = os.path.join(base_dir, 'assets', 'upgrade.wav')
        bullet_path = os.path.join(base_dir, 'assets', 'bullet.wav')
        enemy_path = os.path.join(base_dir, 'assets', 'enemy.wav')
        if os.path.exists(tick_path):
            try:
                self.tick = pygame.mixer.Sound(tick_path)
                self.tick.set_volume(self.volume * 0.9)
            except Exception:
                self.tick = None
        if os.path.exists(rain_path):
            try:
                self.rain_sound = pygame.mixer.Sound(rain_path)
                self.rain_sound.set_volume(self.volume * 0.18)
            except Exception:
                self.rain_sound = None
        if os.path.exists(upgrade_path):
            try:
                self.upgrade_snd = pygame.mixer.Sound(upgrade_path)
                self.upgrade_snd.set_volume(self.volume * 0.25)
            except Exception:
                self.upgrade_snd = None
        if os.path.exists(bullet_path):
            try:
                self.bullet_snd = pygame.mixer.Sound(bullet_path)
                self.bullet_snd.set_volume(self.volume * 0.32)
            except Exception:
                self.bullet_snd = None
        if os.path.exists(enemy_path):
            try:
                self.enemy_snd = pygame.mixer.Sound(enemy_path)
                self.enemy_snd.set_volume(self.volume * 0.22)
            except Exception:
                self.enemy_snd = None
        if os.path.exists(bg_path):
            try:
                pygame.mixer.music.load(bg_path)
                pygame.mixer.music.set_volume(self.volume * 0.5)
                if self.bullet_snd:
                    self.bullet_snd.set_volume(self.volume * 0.32)
                if self.enemy_snd:
                    self.enemy_snd.set_volume(self.volume * 0.22)
                
                pygame.mixer.music.play(-1)
                self._current_music_kind = 'bg'
            except Exception:
                pass

    def notify(self, event):
        if event.name == EVENT_TOWER_FIRE:
            pos = None
            pitch = 1.0
            if event.data:
                pos = event.data.get('pos')
                pitch = float(event.data.get('pitch', 1.0))
            if pos:
                if self.debug_sound_logs:
                    print(f"[Sound v={self.volume:.1f} p={pitch:.2f}] 'Pew Pew!' Target: {pos}")
            else:
                if self.debug_sound_logs:
                    print(f"[Sound v={self.volume:.1f} p={pitch:.2f}] 'Pew Pew!'")
            try:
                if self.bullet_snd and self.enabled:
                    self.bullet_snd.play()
            except Exception:
                pass
        elif event.name == EVENT_ENEMY_KILLED:
            if self.debug_sound_logs:
                print(f"[Sound v={self.volume:.1f}] Explosion")
        elif event.name == EVENT_ENEMY_SPAWNED:
            try:
                if self.enemy_snd and self.enabled:
                    self.enemy_snd.play()
            except Exception:
                pass
        elif event.name == EVENT_TOWER_PLACED:
            if self.debug_sound_logs:
                print(f"[Sound v={self.volume:.1f}] Tower placed: {event.data['pos']}")
        elif event.name == EVENT_SOUND_VOLUME_CHANGED:
            v = max(0.0, min(1.0, float(event.data.get('volume', 1.0))))
            self.volume = v
            try:
                if self.tick:
                    self.tick.set_volume(self.volume * 0.6)
                if self.rain_sound:
                    self.rain_sound.set_volume(self.volume * 0.18)
                pygame.mixer.music.set_volume(self.volume * 0.5)
            except Exception:
                pass
        elif event.name == EVENT_SOUND_TOGGLE:
            self.enabled = bool(event.data.get('enabled', True))
            try:
                if self.enabled:
                    pygame.mixer.music.set_volume(self.volume * 0.5)
                    if self.rain_sound and getattr(self, '_last_state', None) in ('playing', 'paused'):
                        if not getattr(self, 'rain_playing', False):
                            self.rain_sound.play(loops=-1)
                            self.rain_playing = True
                else:
                    pygame.mixer.music.set_volume(0.0)
                    if self.rain_sound and getattr(self, 'rain_playing', False):
                        self.rain_sound.stop()
                        self.rain_playing = False
            except Exception:
                pass
        elif event.name == EVENT_STATE_CHANGED:
            st = event.data.get('state') if event.data else None
            self._last_state = st
            try:
                kind = 'bg' if st in ('menu','settings') else ('war' if st in ('playing','paused') else None)
                if kind and self.enabled:
                    path = self._bg_music_path if kind=='bg' else self._war_music_path
                    if path and self._current_music_kind != kind:
                        pygame.mixer.music.load(path)
                        pygame.mixer.music.set_volume(self.volume * 0.5)
                        pygame.mixer.music.play(-1)
                        self._current_music_kind = kind
                else:
                    pygame.mixer.music.stop()
                    self._current_music_kind = None
                if self.rain_sound:
                    if self.enabled and st in ('playing', 'paused'):
                        if not getattr(self, 'rain_playing', False):
                            self.rain_sound.play(loops=-1)
                            self.rain_playing = True
                    else:
                        if getattr(self, 'rain_playing', False):
                            self.rain_sound.stop()
                            self.rain_playing = False
            except Exception:
                pass
        elif event.name == EVENT_BOSS_NEAR:
            d = event.data.get('dist', None)
            if d is not None:
                if self.debug_sound_logs:
                    print(f"[Ambience] Boss approaching (d={int(d)})")
        elif event.name == EVENT_UI_HOVER:
            pass
        elif event.name == EVENT_MOUSE_CLICK:
            try:
                pass
            except Exception:
                pass
        elif event.name == EVENT_UI_CLICK:
            try:
                if self.tick and self.enabled:
                    now = pygame.time.get_ticks()
                    last = getattr(self, '_click_last_ms', 0)
                    if now - last >= 120:
                        self._click_last_ms = now
                        self.tick.play()
            except Exception:
                pass
        elif event.name == EVENT_TOWER_UPGRADED:
            try:
                if self.upgrade_snd and self.enabled:
                    self.upgrade_snd.play()
            except Exception:
                pass
