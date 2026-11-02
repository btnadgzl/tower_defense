from __future__ import annotations
from typing import Any, Protocol, List


class Event:
    """Lightweight event object carrying a name and optional payload."""
    def __init__(self, name: str, data: Any | None = None) -> None:
        self.name: str = name
        self.data: Any | None = data

EVENT_ENEMY_KILLED = "EnemyKilled"
EVENT_ENEMY_SPAWNED = "EnemySpawned"
EVENT_TOWER_FIRE = "TowerFire"
EVENT_MANUAL_FIRE = "ManualFire"
EVENT_TOWER_PLACED = "TowerPlaced"
EVENT_PATH_SET = "PathSet"
EVENT_UPGRADE_TOWER = "UpgradeTower"
EVENT_TOWER_UPGRADED = "TowerUpgraded"
EVENT_COINS_UPDATED = "CoinsUpdated"
EVENT_TOGGLE_UPGRADE_PANEL = "ToggleUpgradePanel"
EVENT_MOUSE_CLICK = "MouseClick"
EVENT_TOGGLE_PAUSE = "TogglePause"
EVENT_GAME_OVER = "GameOver"
EVENT_QUIT = "Quit"
EVENT_SOUND_VOLUME_CHANGED = "SoundVolumeChanged"
EVENT_MUSIC_VOLUME_CHANGED = "MusicVolumeChanged"
EVENT_BOSS_NEAR = "BossNear"
EVENT_UI_HOVER = "UiHover"
EVENT_UI_CLICK = "UiClick"
EVENT_SOUND_TOGGLE = "SoundToggle"
EVENT_STATE_CHANGED = "StateChanged"
EVENT_ULTI_USED = "UltiUsed"
EVENT_TOGGLE_UPGRADE_DEBUG = "ToggleUpgradeDebug"
EVENT_UPGRADE_DEBUG_ADJUST = "UpgradeDebugAdjust"
EVENT_UPGRADE_DEBUG_SAVE = "UpgradeDebugSave"
EVENT_UPGRADE_DEBUG_SELECT_TYPE = "UpgradeDebugSelectType"
EVENT_UPGRADE_DEBUG_TOGGLE_LIMITS = "UpgradeDebugToggleLimits"
EVENT_TOGGLE_MENU_DEBUG = "ToggleMenuDebug"
EVENT_TOGGLE_SETTINGS_DEBUG = "ToggleSettingsDebug"
EVENT_TOGGLE_GO_DEBUG = "ToggleGoDebug"
EVENT_TOGGLE_PAUSED_DEBUG = "TogglePausedDebug"
EVENT_TOGGLE_HUD_DEBUG = "ToggleHudDebug"
EVENT_TOGGLE_DEBUG_RESIZE_MODE = "ToggleDebugResizeMode"

class EventListener(Protocol):
    def notify(self, event: Event) -> None: ...


class EventManager:
    """Simple observer hub for dispatching events to registered listeners."""
    def __init__(self) -> None:
        self.listeners: List[EventListener] = []

    def register(self, listener: EventListener) -> None:
        self.listeners.append(listener)

    def post(self, event: Event) -> None:
        for listener in list(self.listeners):
            listener.notify(event)
