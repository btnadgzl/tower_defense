from __future__ import annotations
import json
import os
from typing import Any, Dict

# --- Display & Virtual Canvas Constants ---
BASE_WIDTH = 1280
BASE_HEIGHT = 720
PIXEL_SCALE = 4
VIRTUAL_WIDTH = BASE_WIDTH // PIXEL_SCALE   # 320
VIRTUAL_HEIGHT = BASE_HEIGHT // PIXEL_SCALE # 180
FPS = 60

# --- Difficulty Multipliers ---
DIFFICULTY_PROFILES: Dict[str, Dict[str, Any]] = {
    "easy": {
        "label": "Easy",
        "enemy_hp_mult": 0.80,
        "enemy_speed_mult": 0.90,
        "starting_gold": 260,
        "gold_reward_mult": 1.20,
        "castle_hp": 120,
    },
    "normal": {
        "label": "Normal",
        "enemy_hp_mult": 1.00,
        "enemy_speed_mult": 1.00,
        "starting_gold": 200,
        "gold_reward_mult": 1.00,
        "castle_hp": 100,
    },
    "hard": {
        "label": "Hard",
        "enemy_hp_mult": 1.30,
        "enemy_speed_mult": 1.10,
        "starting_gold": 160,
        "gold_reward_mult": 0.90,
        "castle_hp": 80,
    },
}

# --- Tower Definitions (4 Fantasy Archetypes x 3 Upgrade Tiers) ---
TOWER_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "archer": {
        "name": "Archer Tower",
        "short_name": "Archer",
        "desc": "Fast single-target shots with high critical strike chance.",
        "damage_type": "physical",
        "color": (90, 195, 95),
        "levels": [
            {
                "level": 1,
                "cost": 70,
                "damage": 14,
                "range": 175,
                "fire_rate_ms": 580,
                "proj_speed": 480.0,
                "crit_chance": 0.10,
            },
            {
                "level": 2,
                "cost": 110,
                "damage": 24,
                "range": 205,
                "fire_rate_ms": 460,
                "proj_speed": 540.0,
                "crit_chance": 0.18,
            },
            {
                "level": 3,
                "cost": 165,
                "damage": 40,
                "range": 240,
                "fire_rate_ms": 350,
                "proj_speed": 620.0,
                "crit_chance": 0.28,
            },
        ],
    },
    "artillery": {
        "name": "Royal Artillery",
        "short_name": "Artillery",
        "desc": "Fires parabolic mortar shells dealing wide Area of Effect (AoE) damage.",
        "damage_type": "explosive",
        "color": (230, 130, 60),
        "levels": [
            {
                "level": 1,
                "cost": 100,
                "damage": 28,
                "range": 165,
                "fire_rate_ms": 1650,
                "proj_speed": 300.0,
                "splash_radius": 62,
            },
            {
                "level": 2,
                "cost": 145,
                "damage": 48,
                "range": 190,
                "fire_rate_ms": 1450,
                "proj_speed": 330.0,
                "splash_radius": 78,
            },
            {
                "level": 3,
                "cost": 210,
                "damage": 82,
                "range": 220,
                "fire_rate_ms": 1250,
                "proj_speed": 360.0,
                "splash_radius": 96,
            },
        ],
    },
    "frost": {
        "name": "Frost Spire",
        "short_name": "Frost",
        "desc": "Unleashes an icy nova that deals magic damage and slows enemies.",
        "damage_type": "magic",
        "color": (85, 200, 245),
        "levels": [
            {
                "level": 1,
                "cost": 85,
                "damage": 11,
                "range": 155,
                "fire_rate_ms": 950,
                "proj_speed": 400.0,
                "slow_factor": 0.40,
                "slow_duration_ms": 2200,
                "splash_radius": 45,
            },
            {
                "level": 2,
                "cost": 125,
                "damage": 20,
                "range": 180,
                "fire_rate_ms": 820,
                "proj_speed": 440.0,
                "slow_factor": 0.52,
                "slow_duration_ms": 2800,
                "splash_radius": 60,
            },
            {
                "level": 3,
                "cost": 180,
                "damage": 34,
                "range": 205,
                "fire_rate_ms": 700,
                "proj_speed": 480.0,
                "slow_factor": 0.65,
                "slow_duration_ms": 3500,
                "splash_radius": 75,
            },
        ],
    },
    "lightning": {
        "name": "Arcane Obelisk",
        "short_name": "Arcane",
        "desc": "Strikes with armor-piercing chain lightning across multiple targets.",
        "damage_type": "magic",
        "color": (190, 110, 250),
        "levels": [
            {
                "level": 1,
                "cost": 115,
                "damage": 32,
                "range": 170,
                "fire_rate_ms": 1250,
                "proj_speed": 900.0,
                "chain_targets": 2,
                "chain_range": 95,
            },
            {
                "level": 2,
                "cost": 160,
                "damage": 55,
                "range": 195,
                "fire_rate_ms": 1080,
                "proj_speed": 900.0,
                "chain_targets": 3,
                "chain_range": 115,
            },
            {
                "level": 3,
                "cost": 230,
                "damage": 92,
                "range": 225,
                "fire_rate_ms": 920,
                "proj_speed": 900.0,
                "chain_targets": 4,
                "chain_range": 135,
            },
        ],
    },
}

# --- Enemy Archetypes ---
ENEMY_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "goblin": {
        "name": "Goblin Scout",
        "hp": 48,
        "speed": 78.0,
        "armor": 0.0,       # 0% physical reduction
        "magic_res": 0.0,
        "reward": 12,
        "castle_damage": 6,
        "scale": 1.0,
        "boss": False,
    },
    "orc": {
        "name": "Orc Warrior",
        "hp": 115,
        "speed": 52.0,
        "armor": 0.15,      # 15% physical reduction
        "magic_res": 0.0,
        "reward": 18,
        "castle_damage": 10,
        "scale": 1.15,
        "boss": False,
    },
    "warg": {
        "name": "Shadow Warg",
        "hp": 65,
        "speed": 104.0,
        "armor": 0.0,
        "magic_res": 0.15,
        "reward": 15,
        "castle_damage": 8,
        "scale": 1.05,
        "boss": False,
    },
    "knight": {
        "name": "Dark Knight",
        "hp": 240,
        "speed": 38.0,
        "armor": 0.50,      # 50% physical armor -> vulnerable to magic/artillery
        "magic_res": 0.0,
        "reward": 28,
        "castle_damage": 16,
        "scale": 1.25,
        "boss": False,
    },
    "boss_golem": {
        "name": "Ancient Stone Golem",
        "hp": 1150,
        "speed": 28.0,
        "armor": 0.35,
        "magic_res": 0.15,
        "reward": 120,
        "castle_damage": 40,
        "scale": 1.65,
        "boss": True,
    },
}

# --- Active Kingdom Spells ---
SPELLS_CONFIG: Dict[str, Dict[str, Any]] = {
    "meteor": {
        "key": "Q",
        "name": "Meteor Shower",
        "cooldown_ms": 22000,
        "damage": 140,
        "radius": 110,
    },
    "blizzard": {
        "key": "W",
        "name": "Royal Blizzard",
        "cooldown_ms": 26000,
        "damage": 45,
        "slow_factor": 0.70,
        "slow_duration_ms": 4500,
        "castle_heal": 15,
    },
}

DEFAULTS: Dict[str, Any] = {
    "music_volume": 0.5,
    "sfx_volume": 0.7,
    "fullscreen": False,
    "show_fps": True,
    "difficulty": "normal",
    "high_score": 0,
    "best_wave": 1,
    "controls": {
        "spell_meteor": 113,   # K_q
        "spell_blizzard": 119, # K_w
        "speed_toggle": 32,    # K_SPACE
        "pause": 27,           # K_ESCAPE
    },
}


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def load_settings(base_dir: str) -> Dict[str, Any]:
    path = os.path.join(base_dir, "settings.json")
    cfg: Dict[str, Any] = dict(DEFAULTS)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                cfg.update(data)
        except Exception:
            pass
    cfg["music_volume"] = float(_clamp(float(cfg.get("music_volume", DEFAULTS["music_volume"])), 0.0, 1.0))
    cfg["sfx_volume"] = float(_clamp(float(cfg.get("sfx_volume", DEFAULTS["sfx_volume"])), 0.0, 1.0))
    cfg["fullscreen"] = bool(cfg.get("fullscreen", DEFAULTS["fullscreen"]))
    cfg["show_fps"] = bool(cfg.get("show_fps", DEFAULTS["show_fps"]))
    diff = str(cfg.get("difficulty", DEFAULTS["difficulty"])).lower()
    if diff not in DIFFICULTY_PROFILES:
        diff = "normal"
    cfg["difficulty"] = diff
    cfg["high_score"] = int(cfg.get("high_score", 0))
    cfg["best_wave"] = int(cfg.get("best_wave", 1))
    if not isinstance(cfg.get("controls"), dict):
        cfg["controls"] = dict(DEFAULTS["controls"])
    return cfg


def save_settings(base_dir: str, cfg: Dict[str, Any]) -> None:
    path = os.path.join(base_dir, "settings.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
