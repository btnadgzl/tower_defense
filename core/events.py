import pygame

class Event:
    def __init__(self, name, data=None):
        self.name = name
        self.data = data

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
EVENT_BOSS_NEAR = "BossNear"
EVENT_UI_HOVER = "UiHover"
EVENT_UI_CLICK = "UiClick"
EVENT_SOUND_TOGGLE = "SoundToggle"
EVENT_STATE_CHANGED = "StateChanged"

class EventManager:
    def __init__(self):
        self.listeners = []

    def register(self, listener):
        self.listeners.append(listener)

    def post(self, event):
        for listener in self.listeners:
            listener.notify(event)
