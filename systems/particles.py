from __future__ import annotations
import math
import random
from typing import List, Tuple, Dict, Any, Optional
import pygame
from graphics import palette as pal
from graphics.ui_kit import draw_text_shadow


class ParticleSystem:
    """Advanced procedural pixel-art FX system: multi-stage billowing fireballs, dual shockwaves, shrapnel & combat text."""

    def __init__(self) -> None:
        self.particles: List[Dict[str, Any]] = []
        self.floating_texts: List[Dict[str, Any]] = []
        self.shockwaves: List[Dict[str, Any]] = []
        self.fireballs: List[Dict[str, Any]] = []

    def clear(self) -> None:
        self.particles.clear()
        self.floating_texts.clear()
        self.shockwaves.clear()
        self.fireballs.clear()

    # ------------------------------------------------------------------
    # HIT SPARKS
    # ------------------------------------------------------------------
    def spawn_hit(
        self,
        pos: Tuple[float, float],
        color: Tuple[int, int, int] = pal.FIRE_LIGHT,
        count: int = 8,
    ) -> None:
        x, y = float(pos[0]), float(pos[1])
        for _ in range(count):
            ang = random.uniform(0.0, math.tau)
            spd = random.uniform(55.0, 160.0)
            self.particles.append({
                "x": x,
                "y": y,
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd - 25.0,
                "gravity": 190.0,
                "size": random.choice([3, 4, 5]),
                "color": color,
                "outline": True,
                "ttl": random.uniform(200.0, 380.0),
                "max_ttl": 380.0,
            })

    # ------------------------------------------------------------------
    # MULTI-STAGE EXPLOSION (ARTILLERY, METEOR, CASTLE BREACH)
    # ------------------------------------------------------------------
    def spawn_explosion(
        self,
        pos: Tuple[float, float],
        radius: float = 65.0,
        kind: str = "fire",
    ) -> None:
        """Spawns a multi-stage procedural pixel explosion: white-hot flash -> expanding fiery lobes -> billowy smoke plume."""
        x, y = float(pos[0]), float(pos[1])
        rad = max(24.0, float(radius))

        # 1. Dual Shockwaves: Fast outer vapor concussion ring + intense inner fire wave
        self.shockwaves.append({
            "x": x,
            "y": y,
            "max_r": rad * 1.35,
            "color": (255, 255, 255) if kind == "fire" else pal.FROST_CORE,
            "width": 2,
            "ttl": 220.0,
            "max_ttl": 220.0,
        })
        self.shockwaves.append({
            "x": x,
            "y": y,
            "max_r": rad * 0.95,
            "color": pal.FIRE_CORE if kind == "fire" else pal.FROST_LIGHT,
            "width": 4,
            "ttl": 340.0,
            "max_ttl": 340.0,
        })

        # 2. Multi-Lobe Expanding Fireball & Billowing Smoke Plume
        num_lobes = 8
        lobes = []
        for i in range(num_lobes):
            ang = i * (math.tau / num_lobes) + random.uniform(-0.25, 0.25)
            dist_pct = random.uniform(0.20, 0.48)
            lobes.append({
                "angle": ang,
                "dist_pct": dist_pct,
                "scale": random.uniform(0.48, 0.70),
            })
        # Center core lobe
        lobes.append({"angle": 0.0, "dist_pct": 0.0, "scale": 0.78})

        self.fireballs.append({
            "x": x,
            "y": y,
            "max_r": rad,
            "lobes": lobes,
            "kind": kind,
            "ttl": 560.0,
            "max_ttl": 560.0,
        })

        # 3. High-velocity fiery sparks / glowing embers with smoke trails
        spark_colors = (
            [pal.FIRE_CORE, pal.GOLD_SHINE, pal.FIRE_LIGHT, pal.FIRE_MID]
            if kind == "fire"
            else [pal.FROST_CORE, pal.FROST_LIGHT, (220, 245, 255)]
        )
        for _ in range(30):
            ang = random.uniform(0.0, math.tau)
            spd = random.uniform(65.0, rad * 3.8)
            self.particles.append({
                "x": x + random.uniform(-4, 4),
                "y": y + random.uniform(-4, 4),
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd - random.uniform(30.0, 75.0),
                "gravity": 180.0,
                "size": random.choice([3, 4, 5]),
                "color": random.choice(spark_colors),
                "outline": True,
                "ttl": random.uniform(320.0, 580.0),
                "max_ttl": 580.0,
            })

        # 4. Flying solid rock / dirt shrapnel debris
        debris_colors = [pal.STONE_DARK, pal.STONE_MID, pal.OUTLINE_DARK, pal.PATH_DIRT_DARK]
        for _ in range(11):
            ang = random.uniform(-math.pi * 0.9, -math.pi * 0.1)
            spd = random.uniform(50.0, rad * 2.3)
            self.particles.append({
                "x": x + random.uniform(-6, 6),
                "y": y + random.uniform(-6, 6),
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd,
                "gravity": 280.0,
                "size": random.choice([4, 6, 7]),
                "color": random.choice(debris_colors),
                "outline": True,
                "ttl": random.uniform(380.0, 680.0),
                "max_ttl": 680.0,
            })

        # 5. Rising dark smoke particles that drift upward
        for _ in range(9):
            ang = random.uniform(-math.pi * 0.8, -math.pi * 0.2)
            spd = random.uniform(20.0, rad * 0.9)
            self.particles.append({
                "x": x + random.uniform(-10, 10),
                "y": y + random.uniform(-8, 8),
                "vx": math.cos(ang) * spd * 0.4,
                "vy": math.sin(ang) * spd - 32.0,
                "gravity": -15.0,  # Negative gravity for smoke buoyancy!
                "size": random.choice([6, 8, 11]),
                "color": random.choice([pal.STONE_DARK, pal.ASH_MID, pal.UI_BG_DARK]),
                "outline": False,
                "ttl": random.uniform(520.0, 880.0),
                "max_ttl": 880.0,
            })

    # ------------------------------------------------------------------
    # FROST NOVA
    # ------------------------------------------------------------------
    def spawn_frost_nova(self, pos: Tuple[float, float], radius: float = 55.0) -> None:
        self.spawn_explosion(pos, radius, kind="frost")

    # ------------------------------------------------------------------
    # HOLY BURST (SIR ROLAND'S HOLY JUDGMENT)
    # ------------------------------------------------------------------
    def spawn_holy_burst(self, pos: Tuple[float, float], radius: float = 85.0) -> None:
        x, y = float(pos[0]), float(pos[1])
        rad = float(radius)

        # Dual radiant rings
        self.shockwaves.append({
            "x": x,
            "y": y,
            "max_r": rad * 1.35,
            "color": pal.GOLD_SHINE,
            "width": 3,
            "ttl": 320.0,
            "max_ttl": 320.0,
        })
        self.shockwaves.append({
            "x": x,
            "y": y,
            "max_r": rad * 0.85,
            "color": pal.GOLD_LIGHT,
            "width": 5,
            "ttl": 420.0,
            "max_ttl": 420.0,
        })

        # Radiant Sunburst light pillars / rays
        ray_colors = [pal.GOLD_SHINE, pal.UI_TEXT_WHITE, pal.GOLD_LIGHT]
        for i in range(18):
            ang = i * (math.tau / 18.0)
            spd = random.uniform(70.0, rad * 2.8)
            self.particles.append({
                "x": x,
                "y": y,
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd - 15.0,
                "gravity": 40.0,
                "size": random.choice([4, 6]),
                "color": random.choice(ray_colors),
                "outline": True,
                "ttl": random.uniform(350.0, 600.0),
                "max_ttl": 600.0,
            })

    # ------------------------------------------------------------------
    # BUILDING / UPGRADE SPARKLES
    # ------------------------------------------------------------------
    def spawn_build_sparkles(self, pos: Tuple[float, float], color: Tuple[int, int, int] = pal.GOLD_SHINE) -> None:
        x, y = float(pos[0]), float(pos[1])
        self.shockwaves.append({
            "x": x,
            "y": y,
            "max_r": 46.0,
            "color": color,
            "width": 2,
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
                "outline": True,
                "ttl": random.uniform(320.0, 580.0),
                "max_ttl": 580.0,
            })

    # ------------------------------------------------------------------
    # FLOATING COMBAT TEXT
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    def update(self, dt_ms: float) -> None:
        dt_s = dt_ms / 1000.0

        for fb in list(self.fireballs):
            fb["ttl"] -= dt_ms
            if fb["ttl"] <= 0:
                self.fireballs.remove(fb)

        for sw in list(self.shockwaves):
            sw["ttl"] -= dt_ms
            if sw["ttl"] <= 0:
                self.shockwaves.remove(sw)

        for p in list(self.particles):
            p["ttl"] -= dt_ms
            if p["ttl"] <= 0:
                self.particles.remove(p)
                continue
            p["vy"] += p.get("gravity", 0.0) * dt_s
            p["x"] += p["vx"] * dt_s
            p["y"] += p["vy"] * dt_s

        for ft in list(self.floating_texts):
            ft["ttl"] -= dt_ms
            if ft["ttl"] <= 0:
                self.floating_texts.remove(ft)
                continue
            ft["y"] += ft["vy"] * dt_s

    # ------------------------------------------------------------------
    # RENDER PIPELINE
    # ------------------------------------------------------------------
    def draw(
        self,
        surface: pygame.Surface,
        camera_offset: Tuple[int, int],
        font_small: pygame.font.Font,
        font_mid: pygame.font.Font,
    ) -> None:
        ox, oy = camera_offset

        # 1. Shockwaves (expanding concussion waves)
        for sw in self.shockwaves:
            progress = 1.0 - max(0.0, sw["ttl"] / sw["max_ttl"])
            r = max(4, int(sw["max_r"] * (progress ** 0.82)))
            w = max(1, int(sw.get("width", 3) * (1.0 - progress)))
            pygame.draw.circle(surface, sw["color"], (int(sw["x"] + ox), int(sw["y"] + oy)), r, w)

        # 2. Multi-Stage Billowing Pixel Fireballs & Smoke Plumes
        for fb in self.fireballs:
            self._draw_fireball(surface, fb, ox, oy)

        # 3. Crisp square pixel particles & flying shrapnel
        for p in self.particles:
            ratio = max(0.2, p["ttl"] / p["max_ttl"])
            sz = max(2, int(p["size"] * ratio))
            px = int(p["x"] + ox) - sz // 2
            py = int(p["y"] + oy) - sz // 2
            if p.get("outline", False):
                pygame.draw.rect(surface, pal.OUTLINE_DARK, (px - 1, py - 1, sz + 2, sz + 2))
            pygame.draw.rect(surface, p["color"], (px, py, sz, sz))

        # 4. Floating Combat Text
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

    @staticmethod
    def _draw_fireball(surface: pygame.Surface, fb: Dict[str, Any], ox: int, oy: int) -> None:
        """Renders unified procedural multi-lobe pixel fireball cluster with crisp outlines and smoke transition."""
        t = 1.0 - max(0.0, fb["ttl"] / fb["max_ttl"])
        base_r = fb["max_r"]
        kind = fb.get("kind", "fire")
        cx = fb["x"] + ox
        # Buoyancy: smoke drifts upward as it expands
        cy = fb["y"] + oy - (34.0 * (t ** 1.35))

        if t < 0.28:
            growth = t / 0.28
            cur_r = base_r * (0.35 + 0.65 * (growth ** 0.65))
            body_col = pal.FIRE_MID if kind == "fire" else pal.FROST_MID
            core_col: Optional[Tuple[int, int, int]] = pal.FIRE_CORE if kind == "fire" else pal.FROST_CORE
        elif t < 0.60:
            progress = (t - 0.28) / 0.32
            cur_r = base_r * (1.0 + 0.16 * progress)
            body_col = (56, 48, 60) if kind == "fire" else pal.STONE_MID
            core_col = pal.FIRE_DARK if kind == "fire" else pal.FROST_LIGHT
        else:
            progress = (t - 0.60) / 0.40
            cur_r = base_r * (1.16 - 0.40 * progress)
            body_col = (42, 36, 46) if kind == "fire" else pal.STONE_DARK
            core_col = None

        lobe_data = []
        for lobe in fb["lobes"]:
            lr = max(3, int(cur_r * lobe["scale"]))
            dist = cur_r * lobe["dist_pct"]
            ang = lobe["angle"]
            lx = int(cx + math.cos(ang) * dist)
            ly = int(cy + math.sin(ang) * dist)
            lobe_data.append((lx, ly, lr))

        # Layer 1: Outlines for all lobes (merges into a unified cartoon cloud contour!)
        for lx, ly, lr in lobe_data:
            pygame.draw.circle(surface, pal.OUTLINE_DARK, (lx, ly), lr + 2)

        # Layer 2: Solid body fill for all lobes
        for lx, ly, lr in lobe_data:
            pygame.draw.circle(surface, body_col, (lx, ly), lr)

        # Layer 3: Inner fiery core / glowing highlight
        if core_col is not None:
            for lx, ly, lr in lobe_data:
                if lr >= 5:
                    pygame.draw.circle(surface, core_col, (lx, ly - 1), max(2, int(lr * 0.52)))

        # Layer 4: Specular white-hot centers during initial blast
        if t < 0.22 and kind == "fire":
            for lx, ly, lr in lobe_data:
                if lr >= 7:
                    pygame.draw.circle(surface, pal.UI_TEXT_WHITE, (lx, ly - 2), max(1, int(lr * 0.28)))
