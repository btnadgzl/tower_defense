from __future__ import annotations
from typing import List, Dict, Any


# 10 Handcrafted Escalating Tactical Waves (plus Endless scaling after Wave 10)
WAVE_SCHEDULE: List[Dict[str, Any]] = [
    {
        "wave": 1,
        "title": "Goblin Vanguard",
        "groups": [{"type": "goblin", "count": 8, "interval_ms": 1200}],
        "clear_bonus": 35,
    },
    {
        "wave": 2,
        "title": "Orc Raiding Party",
        "groups": [
            {"type": "goblin", "count": 6, "interval_ms": 1000},
            {"type": "orc", "count": 4, "interval_ms": 1500},
        ],
        "clear_bonus": 45,
    },
    {
        "wave": 3,
        "title": "Shadow Warg Pack",
        "groups": [
            {"type": "warg", "count": 8, "interval_ms": 750},
            {"type": "orc", "count": 4, "interval_ms": 1400},
        ],
        "clear_bonus": 55,
    },
    {
        "wave": 4,
        "title": "Iron Vanguard",
        "groups": [
            {"type": "orc", "count": 6, "interval_ms": 1200},
            {"type": "knight", "count": 3, "interval_ms": 1900},
            {"type": "goblin", "count": 8, "interval_ms": 700},
        ],
        "clear_bonus": 65,
    },
    {
        "wave": 5,
        "title": "BOSS: Ancient Stone Golem",
        "groups": [
            {"type": "goblin", "count": 8, "interval_ms": 800},
            {"type": "boss_golem", "count": 1, "interval_ms": 2500},
            {"type": "orc", "count": 5, "interval_ms": 1200},
        ],
        "clear_bonus": 100,
    },
    {
        "wave": 6,
        "title": "Warg Blitz",
        "groups": [
            {"type": "warg", "count": 12, "interval_ms": 620},
            {"type": "knight", "count": 4, "interval_ms": 1650},
        ],
        "clear_bonus": 80,
    },
    {
        "wave": 7,
        "title": "Armored Siege",
        "groups": [
            {"type": "knight", "count": 6, "interval_ms": 1500},
            {"type": "orc", "count": 8, "interval_ms": 1050},
            {"type": "warg", "count": 8, "interval_ms": 650},
        ],
        "clear_bonus": 90,
    },
    {
        "wave": 8,
        "title": "Dark Legion",
        "groups": [
            {"type": "warg", "count": 10, "interval_ms": 580},
            {"type": "knight", "count": 6, "interval_ms": 1400},
            {"type": "goblin", "count": 14, "interval_ms": 520},
        ],
        "clear_bonus": 105,
    },
    {
        "wave": 9,
        "title": "Royal Gate Assault",
        "groups": [
            {"type": "knight", "count": 8, "interval_ms": 1300},
            {"type": "orc", "count": 10, "interval_ms": 900},
            {"type": "warg", "count": 12, "interval_ms": 550},
        ],
        "clear_bonus": 120,
    },
    {
        "wave": 10,
        "title": "FINAL WAVE: Twin Stone Golems",
        "groups": [
            {"type": "knight", "count": 5, "interval_ms": 1300},
            {"type": "boss_golem", "count": 1, "interval_ms": 2600},
            {"type": "warg", "count": 10, "interval_ms": 600},
            {"type": "boss_golem", "count": 1, "interval_ms": 2500},
        ],
        "clear_bonus": 200,
    },
]


class WaveManager:
    """Manages wave preparation countdowns, early wave call bonuses, and enemy spawn queues."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.current_wave: int = 0
        self.max_campaign_waves: int = len(WAVE_SCHEDULE)
        self.state: str = "prep"  # 'prep', 'spawning', 'combat'
        self.prep_timer_ms: float = 12000.0
        self.prep_duration_ms: float = 12000.0
        self.spawn_queue: List[Dict[str, Any]] = []
        self.spawn_timer_ms: float = 0.0
        self.wave_title: str = WAVE_SCHEDULE[0]["title"]

    def get_wave_config(self, wave_num: int) -> Dict[str, Any]:
        if 1 <= wave_num <= len(WAVE_SCHEDULE):
            return WAVE_SCHEDULE[wave_num - 1]
        # Endless wave scaling beyond Wave 10
        extra = wave_num - len(WAVE_SCHEDULE)
        return {
            "wave": wave_num,
            "title": f"Endless Siege #{extra}",
            "groups": [
                {"type": "warg", "count": 10 + extra * 2, "interval_ms": max(400, 600 - extra * 20)},
                {"type": "knight", "count": 6 + extra * 2, "interval_ms": max(850, 1250 - extra * 30)},
                {"type": "boss_golem", "count": 1 + (extra // 2), "interval_ms": 2200},
            ],
            "clear_bonus": 150 + extra * 25,
        }

    def get_next_wave_preview(self) -> str:
        nxt = self.current_wave + 1
        cfg = self.get_wave_config(nxt)
        return f"Wave {nxt}: {cfg['title']}"

    def start_next_wave(self) -> int:
        """Starts the next wave immediately. Returns early-call gold bonus if called during prep."""
        bonus = 0
        if self.state == "prep" and self.current_wave > 0 and self.prep_timer_ms > 1000:
            bonus = max(5, int(self.prep_timer_ms / 400.0))

        self.current_wave += 1
        cfg = self.get_wave_config(self.current_wave)
        self.wave_title = cfg["title"]
        self.spawn_queue = []
        for grp in cfg["groups"]:
            for _ in range(int(grp["count"])):
                self.spawn_queue.append(
                    {"type": grp["type"], "interval_ms": float(grp["interval_ms"])}
                )
        self.state = "spawning"
        self.spawn_timer_ms = 250.0
        return bonus
