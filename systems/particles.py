from __future__ import annotations
import math
import random
from typing import List, Tuple, Dict, Any
import pygame
from graphics import palette as pal
from graphics.ui_kit import draw_text_shadow


class ParticleSystem:
    """Manages crisp pixel-art square particles, expanding shockwaves, and floating combat text."""

    def __init__(self) -> None:
        self.particles: List[Dict[str, Any]] = []
        self.floating_texts: List[Dict[str, Any]] = []
        self.shockwaves: List[Dict[str, Any]] = []

    def clear(self) -> None:
        self.particles.clear()
        self.floating_texts.clear()
        self.shockwaves.clear()

    def spawn_hit(self, pos: Tuple[float, float], color: Tuple[int, int, int] = pal.FIRE_LIGHT, count: int = 8) -> None:
        x, y = float(pos[0]), float(pos[1])
        for _ in range(count):
            ang = random.uniform(0.0, math.tau)
            spd = random.uniform(45.0, 145.0)
            self.particles.append({
                "x": x,
                "y": y,
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd - 20.0,
                "gravity": 180.0,
                "size": random.choice([3, 4, 5]),
                "color": color,
                "ttl": random.uniform(220.0, 420.0),
                "max_ttl": 420.0,
            })

    def spawn_explosion(self, pos: Tuple[float, float], radius: float = 65.0) -> None:
        x, y = float(pos[0]), float(pos[1])
        self.shockwaves.append({
            "x": x,
            "y": y,
            "max_r": radius,
            "color": pal.FIRE_LIGHT,
            "ttl": 320.0,
            "max_ttl": 320.0,
        })
        cols = [pal.FIRE_CORE, pal.FIRE_LIGHT, pal.FIRE_MID, pal.FIRE_DARK, pal.STONE_DARK]
        for _ in range(22):
            ang = random.uniform(0.0, math.tau)
            spd = random.uniform(30.0, radius * 2.6)
            self.particles.append({
                "x": x + random.uniform(-6, 6),
                "y": y + random.uniform(-6, 6),
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd - 35.0,
                "gravity": 140.0,
                "size": random.choice([4, 6, 8]),
                "color": random.choice(cols),
                "ttl": random.uniform(280.0, 560.0),
                "max_ttl": 560.0,
            })

    def spawn_frost_nova(self, pos: Tuple[float, float], radius: float = 55.0) -> None:
        x, y = float(pos[0]), float(pos[1])
        self.shockwaves.append({
            "x": x,
            "y": y,
            "max_r": radius,
            "color": pal.FROST_LIGHT,
            "ttl": 300.0,
            "max_ttl": 300.0,
        })
        cols = [pal.FROST_CORE, pal.FROST_LIGHT, pal.FROST_MID]
        for _ in range(14):
            ang = random.uniform(0.0, math.tau)
            spd = random.uniform(25.0, radius * 2.0)
            self.particles.append({
                "x": x,
                "y": y,
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd,
                "gravity": 0.0,
                "size": random.choice([3, 5]),
                "color": random.choice(cols),
                "ttl": random.uniform(250.0, 450.0),
                "max_ttl": 450.0,
            })

    def spawn_build_sparkles(self, pos: Tuple[float, float], color: Tuple[int, int, int] = pal.GOLD_SHINE) -> None:
        x, y = float(pos[0]), float(pos[1])
        self.shockwaves.append({
            "x": x,
            "y": y,
            "max_r": 46.0,
            "color": color,
            "ttl": 280.0,
            "max_ttl": 280.0,
        })
        for _ in range(16):
            ang = random.uniform(0.0, math.tau)
            spd = random.uniform(40.0, 120.0)
            self.particles.append({
                "x": x + random.uniform(-10, 10),
                "y": y + random.uniform(-10, 10),
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd - 45.0,
                "gravity": 60.0,
                "size": random.choice([3, 5]),
                "color": random.choice([color, pal.GOLD_LIGHT, pal.UI_TEXT_WHITE]),
                "ttl": random.uniform(320.0, 580.0),
                "max_ttl": 580.0,
            })

    def add_floating_text(
        self,
        pos: Tuple[float, float],
        text: str,
        color: Tuple[int, int, int] = pal.GOLD_SHINE,
        big: bool = False,
        ttl_ms: float = 850.0,
    ) -> None:
        self.floating_texts.append({
            "x": float(pos[0]) + random.uniform(-8.0, 8.0),
            "y": float(pos[1]) - 14.0,
            "vy": -46.0 if not big else -56.0,
            "text": text,
            "color": color,
            "big": big,
            "ttl": ttl_ms,
            "max_ttl": ttl_ms,
        })

    def update(self, dt_ms: float) -> None:
        dt_s = dt_ms / 1000.0
        for p in list(self.particles):
            p["ttl"] -= dt_ms
            if p["ttl"] <= 0:
                self.particles.remove(p)
                continue
            p["vy"] += p.get("gravity", 0.0) * dt_s
            p["x"] += p["vx"] * dt_s
            p["y"] += p["vy"] * dt_s

        for sw in list(self.shockwaves):
            sw["ttl"] -= dt_ms
            if sw["ttl"] <= 0:
                self.shockwaves.remove(sw)

        for ft in list(self.floating_texts):
            ft["ttl"] -= dt_ms
            if ft["ttl"] <= 0:
                self.floating_texts.remove(ft)
                continue
            ft["y"] += ft["vy"] * dt_s

    def draw(
        self,
        surface: pygame.Surface,
        camera_offset: Tuple[int, int],
        font_small: pygame.font.Font,
        font_mid: pygame.font.Font,
    ) -> None:
        ox, oy = camera_offset

        # Shockwaves
        for sw in self.shockwaves:
            p = 1.0 - max(0.0, sw["ttl"] / sw["max_ttl"])
            r = max(4, int(sw["max_r"] * p))
            w = max(2, int(5 * (1.0 - p)))
            pygame.draw.circle(surface, sw["color"], (int(sw["x"] + ox), int(sw["y"] + oy)), r, w)

        # Crisp square pixel particles with dark contour
        for p in self.particles:
            ratio = max(0.2, p["ttl"] / p["max_ttl"])
            sz = max(2, int(p["size"] * ratio))
            px = int(p["x"] + ox) - sz // 2
            py = int(p["y"] + oy) - sz // 2
            pygame.draw.rect(surface, pal.OUTLINE_DARK, (px - 1, py - 1, sz + 2, sz + 2))
            pygame.draw.rect(surface, p["color"], (px, py, sz, sz))

        # Floating text
        for ft in self.floating_texts:
            fnt = font_mid if ft["big"] else font_small
            draw_text_shadow(
                surface,
                fnt,
                ft["text"],
                ft["color"],
                pos=(int(ft["x"] + ox), int(ft["y"] + oy)),
                align="center",
            )

