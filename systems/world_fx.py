from __future__ import annotations
import math
import random
from typing import List, Dict, Tuple, Any
import pygame
from graphics import palette as pal


class WorldEffectsSystem:
    """Manages persistent battlefield decals (scorch craters, ice patches), river flow, and biome particles."""

    MAX_DECALS = 65

    def __init__(self, width: int, height: int, biome: str = "grasslands") -> None:
        self.width = width
        self.height = height
        self.biome = biome
        self.decals: List[Dict[str, Any]] = []
        self.fireflies: List[Dict[str, Any]] = []
        self.leaves: List[Dict[str, Any]] = []
        self.river_ripples: List[Dict[str, Any]] = []
        self._init_ambient_entities()

    def set_biome(self, biome: str) -> None:
        if self.biome != biome:
            self.biome = biome
            self._init_ambient_entities()

    def clear(self) -> None:
        self.decals.clear()
        self._init_ambient_entities()

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self._init_ambient_entities()

    def _init_ambient_entities(self) -> None:
        self.fireflies.clear()
        if self.biome == "frost_tundra":
            ff_colors = [(160, 235, 255), (220, 250, 255), (110, 200, 255)]
            leaf_colors = [pal.FROST_CORE, pal.TUNDRA_HIGHLIGHT, pal.FROST_LIGHT]
        elif self.biome == "volcanic_ash":
            ff_colors = [pal.FIRE_LIGHT, pal.FIRE_MID, pal.LAVA_BRIGHT]
            leaf_colors = [pal.FIRE_MID, pal.FIRE_LIGHT, pal.ASH_HIGHLIGHT]
        else:
            ff_colors = [(255, 225, 110), (135, 255, 165), (120, 220, 255)]
            leaf_colors = [pal.LEAF_LIGHT, pal.GRASS_HIGHLIGHT, pal.LEAF_AUTUMN]

        for _ in range(22):
            self.fireflies.append({
                "x": random.uniform(40.0, self.width - 40.0),
                "y": random.uniform(60.0, self.height - 40.0),
                "vx": random.uniform(-16.0, 16.0),
                "vy": random.uniform(-12.0, 12.0),
                "phase": random.uniform(0.0, math.tau),
                "speed_phase": random.uniform(2.2, 4.5),
                "color": random.choice(ff_colors),
            })

        self.leaves.clear()
        for _ in range(22 if self.biome == "frost_tundra" else 18):
            self.leaves.append({
                "x": random.uniform(0.0, float(self.width)),
                "y": random.uniform(0.0, float(self.height)),
                "vx": random.uniform(12.0, 32.0),
                "vy": random.uniform(-24.0, -10.0) if self.biome == "volcanic_ash" else random.uniform(12.0, 28.0),
                "sway": random.uniform(0.0, math.tau),
                "color": random.choice(leaf_colors),
            })

        self.river_ripples.clear()
        for i in range(26):
            self.river_ripples.append({
                "y_pct": (i / 26.0) + random.uniform(0.0, 0.03),
                "x_off": random.uniform(-0.012, 0.012),
                "len": random.choice([6, 9, 12]),
            })

    # ------------------------------------------------------------------
    # PERSISTENT BATTLEFIELD DECALS
    # ------------------------------------------------------------------
    def add_scorch_crater(self, pos: Tuple[float, float], radius: float = 36.0) -> None:
        r = max(14, min(48, int(radius * 0.52)))
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        c = (r + 2, r + 2)
        pygame.draw.ellipse(surf, (24, 18, 22, 175), (4, int(r * 0.35), r * 2 - 4, int(r * 1.3)))
        pygame.draw.ellipse(surf, (42, 32, 34, 155), (8, int(r * 0.50), r * 2 - 12, int(r * 1.0)))
        for _ in range(5):
            ex = c[0] + random.randint(-r // 2, r // 2)
            ey = c[1] + random.randint(-r // 3, r // 3)
            pygame.draw.rect(surf, (*pal.FIRE_MID, 210), (ex, ey, 3, 3))
        self._push_decal(pos[0], pos[1], surf, ttl_ms=16000.0)

    def add_frost_patch(self, pos: Tuple[float, float], radius: float = 32.0) -> None:
        r = max(12, min(42, int(radius * 0.55)))
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (110, 215, 255, 115), (4, int(r * 0.4), r * 2 - 4, int(r * 1.2)))
        pygame.draw.ellipse(surf, (210, 245, 255, 130), (9, int(r * 0.55), r * 2 - 14, int(r * 0.9)))
        self._push_decal(pos[0], pos[1], surf, ttl_ms=11000.0)

    def add_holy_sigil(self, pos: Tuple[float, float], radius: float = 48.0) -> None:
        """Golden consecrated ground decal left behind by the Paladin's Holy Judgment."""
        r = max(18, min(52, int(radius * 0.55)))
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        c = (r + 2, r + 2)
        pygame.draw.ellipse(surf, (250, 210, 75, 125), (4, int(r * 0.35), r * 2 - 4, int(r * 1.25)), 3)
        pygame.draw.ellipse(surf, (255, 245, 175, 95), (10, int(r * 0.50), r * 2 - 16, int(r * 0.95)))
        pygame.draw.line(surf, (255, 245, 175, 160), (c[0] - r // 2, c[1]), (c[0] + r // 2, c[1]), 2)
        pygame.draw.line(surf, (255, 245, 175, 160), (c[0], c[1] - r // 3), (c[0], c[1] + r // 3), 2)
        self._push_decal(pos[0], pos[1], surf, ttl_ms=10000.0)

    def add_combat_splat(self, pos: Tuple[float, float]) -> None:
        surf = pygame.Surface((16, 12), pygame.SRCALPHA)
        for _ in range(4):
            sx = random.randint(2, 11)
            sy = random.randint(2, 8)
            pygame.draw.rect(surf, (135, 28, 38, 165), (sx, sy, 3, 3))
        self._push_decal(pos[0], pos[1], surf, ttl_ms=9000.0)

    def _push_decal(self, x: float, y: float, surf: pygame.Surface, ttl_ms: float) -> None:
        if len(self.decals) >= self.MAX_DECALS:
            self.decals.pop(0)
        self.decals.append({
            "x": float(x),
            "y": float(y),
            "surf": surf,
            "ttl": ttl_ms,
            "max_ttl": ttl_ms,
        })

    # ------------------------------------------------------------------
    # UPDATE & RENDER
    # ------------------------------------------------------------------
    def update(self, dt_ms: float) -> None:
        dt_s = dt_ms / 1000.0

        for d in list(self.decals):
            d["ttl"] -= dt_ms
            if d["ttl"] <= 0:
                self.decals.remove(d)

        speed_mult = 0.045 if self.biome == "volcanic_ash" else (0.055 if self.biome == "frost_tundra" else 0.085)
        for rp in self.river_ripples:
            rp["y_pct"] = (rp["y_pct"] + dt_s * speed_mult) % 1.0

        for ff in self.fireflies:
            ff["phase"] += dt_s * ff["speed_phase"]
            ff["x"] += (ff["vx"] + math.sin(ff["phase"]) * 8.0) * dt_s
            ff["y"] += (ff["vy"] + math.cos(ff["phase"] * 0.8) * 6.0) * dt_s
            if ff["x"] < 20.0 or ff["x"] > self.width - 20.0:
                ff["vx"] *= -1
            if ff["y"] < 55.0 or ff["y"] > self.height - 25.0:
                ff["vy"] *= -1

        for lf in self.leaves:
            lf["sway"] += dt_s * 3.2
            lf["x"] += (lf["vx"] + math.sin(lf["sway"]) * 12.0) * dt_s
            lf["y"] += lf["vy"] * dt_s
            if self.biome == "volcanic_ash":
                if lf["x"] > self.width + 10 or lf["y"] < -10:
                    lf["x"] = random.uniform(-20.0, self.width * 0.8)
                    lf["y"] = float(self.height + 8)
            else:
                if lf["x"] > self.width + 10 or lf["y"] > self.height + 10:
                    lf["x"] = random.uniform(-20.0, self.width * 0.6)
                    lf["y"] = -8.0

    def draw_ground_layer(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        """Draws animated river/lava/ice ripples and ground decals directly over the terrain map."""
        ox, oy = camera_offset
        rip_col = (
            pal.LAVA_BRIGHT
            if self.biome == "volcanic_ash"
            else (pal.FROST_CORE if self.biome == "frost_tundra" else pal.WATER_FOAM)
        )

        # 1. Animated River / Lava Current (skip under the stone bridge y_pct 0.69..0.80)
        for rp in self.river_ripples:
            yp = rp["y_pct"]
            if 0.69 <= yp <= 0.80:
                continue
            rx_center = self.width * (0.475 + 0.025 * math.sin(yp * math.pi * 2.2) + rp["x_off"])
            rx = int(rx_center + ox)
            ry = int(yp * self.height + oy)
            pygame.draw.line(surface, rip_col, (rx, ry), (rx, ry + rp["len"]), 2)

        # 2. Persistent Battlefield Decals
        for d in self.decals:
            srf: pygame.Surface = d["surf"]
            ratio = max(0.0, min(1.0, d["ttl"] / d["max_ttl"]))
            if ratio < 0.35:
                srf.set_alpha(int(255 * (ratio / 0.35)))
            else:
                srf.set_alpha(255)
            rect = srf.get_rect(center=(int(d["x"] + ox), int(d["y"] + oy)))
            surface.blit(srf, rect)

    def draw_canopy_layer(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        """Draws drifting wind-blown leaves/snowflakes/embers and glowing firefly sprites above entities."""
        ox, oy = camera_offset

        for lf in self.leaves:
            lx = int(lf["x"] + ox)
            ly = int(lf["y"] + oy)
            pygame.draw.rect(surface, pal.OUTLINE_DARK, (lx - 1, ly - 1, 5, 4))
            pygame.draw.rect(surface, lf["color"], (lx, ly, 3, 2))

        for ff in self.fireflies:
            glow = 0.5 + 0.5 * math.sin(ff["phase"])
            if glow > 0.25:
                fx = int(ff["x"] + ox)
                fy = int(ff["y"] + oy)
                pygame.draw.rect(surface, pal.OUTLINE_DARK, (fx - 2, fy - 2, 5, 5))
                pygame.draw.rect(surface, ff["color"], (fx - 1, fy - 1, 3, 3))
