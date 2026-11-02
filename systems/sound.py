from __future__ import annotations
import os
import sys
from typing import Any
import pygame
from core.events import (
    EVENT_TOWER_FIRE,
    EVENT_ENEMY_SPAWNED,
    EVENT_TOWER_BUILT,
    EVENT_TOWER_UPGRADED,
    EVENT_SPELL_CAST,
    EVENT_SOUND_VOLUME_CHANGED,
    EVENT_MUSIC_VOLUME_CHANGED,
    EVENT_SOUND_TOGGLE,
    EVENT_STATE_CHANGED,
    EVENT_UI_CLICK,
    EVENT_GAME_OVER,
)


class SoundSystem:
    """Handles background music and SFX playback with full volume synchronization."""

    def __init__(self, ev_manager: Any, sfx_volume: float = 0.7, music_volume: float = 0.5) -> None:
        self.ev_manager = ev_manager
        self.ev_manager.register(self)
        self.volume = float(sfx_volume)
        self.music_volume = float(music_volume)
        self.enabled = True
        self.rain_playing = False
        self._last_state = None
        self._current_music_kind = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            pass

        base_dir = getattr(sys, "_MEIPASS", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        assets_dir = os.path.join(base_dir, "assets")

        self._bg_music_path = self._existing(os.path.join(assets_dir, "background_effect.wav"))
        self._war_music_path = self._existing(os.path.join(assets_dir, "war_effect.wav"))
        self.tick = self._load_snd(os.path.join(assets_dir, "ui_tick.wav"))
        self.rain_sound = self._load_snd(os.path.join(assets_dir, "rain.wav"))
        self.upgrade_snd = self._load_snd(os.path.join(assets_dir, "upgrade.wav"))
        self.bullet_snd = self._load_snd(os.path.join(assets_dir, "bullet.wav"))
        self.enemy_snd = self._load_snd(os.path.join(assets_dir, "enemy.wav"))
        self.game_over_snd = self._load_snd(os.path.join(assets_dir, "game_over.wav"))

        self._apply_volumes()
        self._play_music("bg")

    @staticmethod
    def _existing(path: str) -> str | None:
        return path if os.path.exists(path) else None

    @staticmethod
    def _load_snd(path: str) -> Any:
        if os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except Exception:
                return None
        return None

    def _apply_volumes(self) -> None:
        eff_sfx = self.volume if self.enabled else 0.0
        eff_mus = self.music_volume if self.enabled else 0.0
        try:
            if self.tick:
                self.tick.set_volume(eff_sfx * 0.65)
            if self.rain_sound:
                self.rain_sound.set_volume(eff_sfx * 0.14)
            if self.upgrade_snd:
                self.upgrade_snd.set_volume(eff_sfx * 0.35)
            if self.bullet_snd:
                self.bullet_snd.set_volume(eff_sfx * 0.26)
            if self.enemy_snd:
                self.enemy_snd.set_volume(eff_sfx * 0.18)
            if self.game_over_snd:
                self.game_over_snd.set_volume(eff_mus * 0.80)
            pygame.mixer.music.set_volume(eff_mus)
        except Exception:
            pass

    def _play_music(self, kind: str | None) -> None:
        if not self.enabled or not kind:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
            self._current_music_kind = None
            return
        path = self._bg_music_path if kind == "bg" else self._war_music_path
        if path and self._current_music_kind != kind:
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(self.music_volume if self.enabled else 0.0)
                pygame.mixer.music.play(-1)
                self._current_music_kind = kind
            except Exception:
                pass

    def notify(self, event: Any) -> None:
        if event.name == EVENT_TOWER_FIRE:
            if self.bullet_snd and self.enabled:
                try:
                    now = pygame.time.get_ticks()
                    if now - getattr(self, "_last_fire_ms", 0) >= 85:
                        self._last_fire_ms = now
                        self.bullet_snd.play()
                except Exception:
                    pass
        elif event.name == EVENT_ENEMY_SPAWNED:
            if self.enemy_snd and self.enabled and event.data.get("boss"):
                try:
                    self.enemy_snd.play()
                except Exception:
                    pass
        elif event.name in (EVENT_TOWER_BUILT, EVENT_TOWER_UPGRADED, EVENT_SPELL_CAST):
            if self.upgrade_snd and self.enabled:
                try:
                    self.upgrade_snd.play()
                except Exception:
                    pass
        elif event.name == EVENT_UI_CLICK:
            if self.tick and self.enabled:
                try:
                    self.tick.play()
                except Exception:
                    pass
        elif event.name == EVENT_SOUND_VOLUME_CHANGED:
            self.volume = max(0.0, min(1.0, float(event.data.get("volume", self.volume))))
            self._apply_volumes()
        elif event.name == EVENT_MUSIC_VOLUME_CHANGED:
            self.music_volume = max(0.0, min(1.0, float(event.data.get("volume", self.music_volume))))
            self._apply_volumes()
        elif event.name == EVENT_SOUND_TOGGLE:
            self.enabled = bool(event.data.get("enabled", True))
            self._apply_volumes()
            if not self.enabled and self.rain_sound and self.rain_playing:
                try:
                    self.rain_sound.stop()
                    self.rain_playing = False
                except Exception:
                    pass
        elif event.name == EVENT_STATE_CHANGED:
            st = event.data.get("state")
            self._last_state = st
            kind = "bg" if st in ("menu", "settings") else ("war" if st in ("playing", "paused") else None)
            self._play_music(kind)
            if self.rain_sound:
                try:
                    if self.enabled and st in ("playing", "paused"):
                        if not self.rain_playing:
                            self.rain_sound.play(loops=-1)
                            self.rain_playing = True
                    else:
                        if self.rain_playing:
                            self.rain_sound.stop()
                            self.rain_playing = False
                except Exception:
                    pass
        elif event.name == EVENT_GAME_OVER:
            try:
                pygame.mixer.music.stop()
                self._current_music_kind = "go"
                if self.enabled and self.game_over_snd:
                    self.game_over_snd.play()
            except Exception:
                pass

