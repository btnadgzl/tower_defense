from __future__ import annotations
from typing import Any, Protocol, List


class Event:
    """Lightweight event object carrying a name and optional payload."""
    def __init__(self, name: str, data: Any | None = None) -> None:
        self.name: str = name
        self.data: Any | None = data or {}


# --- Core & Lifecycle Events ---
EVENT_QUIT = "Quit"
EVENT_STATE_CHANGED = "StateChanged"
EVENT_GAME_OVER = "GameOver"
EVENT_VICTORY = "Victory"

# --- Gameplay Events ---
EVENT_WAVE_STARTED = "WaveStarted"
EVENT_WAVE_CLEARED = "WaveCleared"
EVENT_ENEMY_SPAWNED = "EnemySpawned"
EVENT_ENEMY_KILLED = "EnemyKilled"
EVENT_ENEMY_HIT = "EnemyHit"
EVENT_ENEMY_REACHED_CASTLE = "EnemyReachedCastle"

# --- Tower, Hero & Ability Events ---
EVENT_TOWER_BUILT = "TowerBuilt"
EVENT_TOWER_UPGRADED = "TowerUpgraded"
EVENT_TOWER_SOLD = "TowerSold"
EVENT_TOWER_FIRE = "TowerFire"
EVENT_SPELL_CAST = "SpellCast"
EVENT_HERO_LEVEL_UP = "HeroLevelUp"
EVENT_HERO_SKILL = "HeroSkill"

# --- Economy & Status Events ---
EVENT_COINS_UPDATED = "CoinsUpdated"
EVENT_CASTLE_HP_UPDATED = "CastleHpUpdated"

# --- UI & Audio Events ---
EVENT_UI_HOVER = "UiHover"
EVENT_UI_CLICK = "UiClick"
EVENT_SOUND_VOLUME_CHANGED = "SoundVolumeChanged"
EVENT_MUSIC_VOLUME_CHANGED = "MusicVolumeChanged"
EVENT_SOUND_TOGGLE = "SoundToggle"


class EventListener(Protocol):
    def notify(self, event: Event) -> None: ...


class EventManager:
    """Observer hub for dispatching events to registered listeners."""
    def __init__(self) -> None:
        self.listeners: List[EventListener] = []

    def register(self, listener: EventListener) -> None:
        if listener not in self.listeners:
            self.listeners.append(listener)

    def unregister(self, listener: EventListener) -> None:
        if listener in self.listeners:
            self.listeners.remove(listener)

    def post(self, event: Event) -> None:
        for listener in list(self.listeners):
            listener.notify(event)
