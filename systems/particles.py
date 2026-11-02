from __future__ import annotations
import math
import random
from typing import List, Tuple, Dict, Any, Optional
import pygame
from graphics import palette as pal
from graphics.ui_kit import draw_text_shadow


class FluidExplosion:
    """High-fidelity procedural fluid explosion engine.
    Simulates supersonic shockwaves, directional ground blast & upward mushroom plume,
    cauliflower-lobed roiling fireball, high-speed incandescent tracer sparks, and buoyant dissipating smoke."""

    def __init__(self, x: float, y: float, radius: float = 65.0, kind: str = "fire") -> None:
        self.x: float = float(x)
        self.y: float = float(y)
        self.base_r: float = max(24.0, float(radius))
        self.kind: str = kind
        self.duration_ms: float = 720.0
        self.elapsed_ms: float = 0.0
        self.alive: bool = True

        # Elemental Palette Configuration
        if self.kind == "frost":
            self.shock_col1 = (215, 248, 255)
            self.shock_col2 = (80, 185, 245)
            self.spark_head = (235, 250, 255)
            self.spark_mid = (100, 210, 255)
            self.spark_tail = (45, 120, 205)
            self.debris_col = (25, 45, 65)
            self.debris_hi = (120, 185, 225)
        elif self.kind == "holy":
            self.shock_col1 = (255, 255, 240)
            self.shock_col2 = (255, 215, 60)
            self.spark_head = (255, 255, 250)
            self.spark_mid = (255, 225, 85)
            self.spark_tail = (215, 160, 30)
            self.debris_col = (45, 38, 25)
            self.debris_hi = (195, 165, 75)
        else:  # "fire"
            self.shock_col1 = (255, 255, 240)
            self.shock_col2 = (255, 160, 35)
            self.spark_head = (255, 255, 230)
            self.spark_mid = (255, 175, 40)
            self.spark_tail = (215, 50, 20)
            self.debris_col = (18, 16, 20)
            self.debris_hi = (70, 65, 75)

        # 1. Asymmetrical Boiling Lobes (Directional Ground Blast + Mushroom Cloud Plume)
        self.lobes: List[Dict[str, Any]] = []
        num_lobes = 10
        for i in range(num_lobes):
            raw_ang = (i / num_lobes) * math.tau
            # Ground reflection bias: deflect downward blast sideways & upward
            if math.sin(raw_ang) > 0.15:
                ang = raw_ang - math.pi * 0.40 if math.cos(raw_ang) > 0 else raw_ang + math.pi * 0.40
            else:
                ang = raw_ang + random.uniform(-0.18, 0.18)

            spd = random.uniform(self.base_r * 1.2, self.base_r * 2.8)
            vy_bias = -random.uniform(self.base_r * 0.6, self.base_r * 1.5)
            scale = random.uniform(0.38, 0.58)

            self.lobes.append({
                "x": self.x + math.cos(ang) * random.uniform(2.0, self.base_r * 0.2),
                "y": self.y + math.sin(ang) * random.uniform(2.0, self.base_r * 0.2),
                "vx": math.cos(ang) * spd * random.uniform(0.7, 1.3),
                "vy": math.sin(ang) * spd + vy_bias,
                "radius": self.base_r * scale,
                "growth": random.uniform(1.8, 2.7),
                "drag": random.uniform(0.85, 0.91),
                "buoyancy": random.uniform(70.0, 120.0),
                "is_core": (i < 3),
                "sub_offset": (random.uniform(-4.0, 4.0), random.uniform(-4.0, 4.0)),
            })

        # Central dense core lobe
        self.lobes.append({
            "x": self.x,
            "y": self.y - 4.0,
            "vx": random.uniform(-10.0, 10.0),
            "vy": -random.uniform(20.0, 50.0),
            "radius": self.base_r * 0.55,
            "growth": 2.2,
            "drag": 0.88,
            "buoyancy": 90.0,
            "is_core": True,
            "sub_offset": (0.0, 0.0),
        })

        # 2. Piercing Starburst Spikes / Flame Tendrils
        self.spikes: List[Dict[str, Any]] = []
        for i in range(12):
            ang = (i / 12) * math.tau + random.uniform(-0.15, 0.15)
            spd = random.uniform(self.base_r * 3.5, self.base_r * 5.8)
            self.spikes.append({
                "ang": ang,
                "dist": 0.0,
                "spd": spd,
                "len": random.uniform(self.base_r * 0.60, self.base_r * 1.0),
                "w": random.uniform(self.base_r * 0.25, self.base_r * 0.40),
                "ttl": random.uniform(180.0, 320.0),
                "max_ttl": 320.0,
            })

        # 3. High-Velocity Shockwaves (Concussion vapor ring + inner heat wave)
        self.shockwaves: List[Dict[str, Any]] = [
            {"max_r": self.base_r * 1.85, "width": 4, "color": self.shock_col1, "duration_ms": 230.0},
            {"max_r": self.base_r * 1.35, "width": 7, "color": self.shock_col2, "duration_ms": 360.0},
        ]

        # 4. Ultra-Fast Incandescent Tracer Sparks
        self.sparks: List[Dict[str, Any]] = []
        num_sparks = 42
        for _ in range(num_sparks):
            ang = random.uniform(0.0, math.tau)
            spd = random.uniform(self.base_r * 5.0, self.base_r * 11.0)
            self.sparks.append({
                "x": self.x,
                "y": self.y,
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd - random.uniform(30.0, 110.0),
                "drag": random.uniform(0.935, 0.970),
                "gravity": 260.0,
                "ttl": random.uniform(340.0, 700.0),
                "max_ttl": 700.0,
                "streak": random.uniform(0.05, 0.08),
                "size": random.choice([2, 3]),
            })

        # 5. Tumbling Shrapnel Debris
        self.debris: List[Dict[str, Any]] = []
        for _ in range(12):
            ang = random.uniform(-math.pi * 0.95, -math.pi * 0.05)
            spd = random.uniform(self.base_r * 3.5, self.base_r * 7.5)
            self.debris.append({
                "x": self.x,
                "y": self.y,
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd - random.uniform(20.0, 60.0),
                "rot": random.uniform(0.0, 360.0),
                "vrot": random.uniform(-900.0, 900.0),
                "size": random.uniform(4.0, 7.5),
                "gravity": 420.0,
                "ttl": random.uniform(450.0, 720.0),
                "max_ttl": 720.0,
            })

    def update(self, dt_ms: float) -> None:
        dt_s = dt_ms / 1000.0
        self.elapsed_ms += dt_ms
        if self.elapsed_ms >= self.duration_ms:
            self.alive = False

        norm_t = min(1.0, self.elapsed_ms / self.duration_ms)

        # Update boiling lobes
        for lb in self.lobes:
            lb["x"] += lb["vx"] * dt_s
            lb["y"] += lb["vy"] * dt_s
            drag = lb["drag"] ** (dt_ms / 16.0)
            lb["vx"] *= drag
            lb["vy"] *= drag
            if norm_t > 0.15:
                lb["vy"] -= lb["buoyancy"] * dt_s

        # Update spikes
        for sp in self.spikes:
            sp["ttl"] -= dt_ms
            sp["dist"] += sp["spd"] * dt_s
            sp["spd"] *= (0.87 ** (dt_ms / 16.0))

        # Update incandescent sparks
        for sp in self.sparks:
            sp["ttl"] -= dt_ms
            sp["vy"] += sp["gravity"] * dt_s
            drag = sp["drag"] ** (dt_ms / 16.0)
            sp["vx"] *= drag
            sp["vy"] *= drag
            sp["x"] += sp["vx"] * dt_s
            sp["y"] += sp["vy"] * dt_s

        # Update shrapnel debris
        for db in self.debris:
            db["ttl"] -= dt_ms
            db["vy"] += db["gravity"] * dt_s
            db["x"] += db["vx"] * dt_s
            db["y"] += db["vy"] * dt_s
            db["rot"] += db["vrot"] * dt_s

    def draw(self, target: pygame.Surface, ox: int = 0, oy: int = 0) -> None:
        norm_t = min(1.0, self.elapsed_ms / self.duration_ms)

        # 1. Soft Shockwaves with Alpha Falloff
        for sw in self.shockwaves:
            prog = min(1.0, self.elapsed_ms / sw["duration_ms"])
            if prog < 1.0:
                cur_r = sw["max_r"] * (1.0 - (1.0 - prog) ** 3.4)
                alpha = int(230 * (1.0 - prog))
                if cur_r > 3 and alpha > 5:
                    sw_surf = pygame.Surface((int(cur_r * 2 + 16), int(cur_r * 2 + 16)), pygame.SRCALPHA)
                    center = int(cur_r + 8)
                    pygame.draw.circle(sw_surf, (*sw["color"][:3], max(1, alpha // 3)), (center, center), int(cur_r), sw["width"] + 3)
                    pygame.draw.circle(sw_surf, (*sw["color"][:3], alpha), (center, center), int(cur_r), max(1, sw["width"] - 1))
                    target.blit(sw_surf, (int(self.x + ox - center), int(self.y + oy - center)), special_flags=pygame.BLEND_ALPHA_SDL2)

        # 2. Volumetric Fluid Fire & Smoke Plume
        max_bound = int(self.base_r * 4.6)
        exp_surf = pygame.Surface((max_bound * 2, max_bound * 2), pygame.SRCALPHA)
        center_x = max_bound
        center_y = max_bound

        lobe_renders = []
        for lb in self.lobes:
            px = center_x + (lb["x"] - self.x)
            py = center_y + (lb["y"] - self.y)
            growth = 1.0 + (lb["growth"] - 1.0) * (norm_t ** 0.54)
            cur_r = max(3.0, lb["radius"] * growth)
            lobe_renders.append((px, py, cur_r, lb["is_core"], lb["sub_offset"]))

        # Color & Alpha Stages
        if self.kind == "frost":
            if norm_t < 0.24:
                alpha = 255
                rim_col = (20, 95, 175, alpha)
                mid_col = (70, 190, 245, alpha)
                cor_col: Optional[Tuple[int, int, int, int]] = (230, 252, 255, alpha)
                smoke_hi: Optional[Tuple[int, int, int, int]] = None
            elif norm_t < 0.52:
                sub_t = (norm_t - 0.24) / 0.28
                alpha = int(250 - 35 * sub_t)
                rim_col = (int(20*(1-sub_t) + 40*sub_t), int(95*(1-sub_t) + 65*sub_t), int(175*(1-sub_t) + 85*sub_t), alpha)
                mid_col = (int(70*(1-sub_t) + 120*sub_t), int(190*(1-sub_t) + 180*sub_t), int(245*(1-sub_t) + 215*sub_t), alpha)
                cor_col = (int(230*(1-sub_t) + 190*sub_t), int(252*(1-sub_t) + 235*sub_t), int(255*(1-sub_t) + 250*sub_t), alpha)
                smoke_hi = None
            elif norm_t < 0.78:
                sub_t = (norm_t - 0.52) / 0.26
                alpha = int(215 * (1.0 - 0.35 * sub_t))
                rim_col = (35, 52, 68, alpha)
                mid_col = (60, 90, 115, alpha)
                smoke_hi = (95, 135, 165, alpha)
                cor_col = (140, 210, 245, int(alpha * (1.0 - sub_t)))
            else:
                sub_t = (norm_t - 0.78) / 0.22
                alpha = int(140 * (1.0 - sub_t))
                rim_col = (28, 42, 54, alpha)
                mid_col = (48, 70, 90, alpha)
                smoke_hi = (75, 105, 130, alpha)
                cor_col = None
        elif self.kind == "holy":
            if norm_t < 0.24:
                alpha = 255
                rim_col = (215, 150, 25, alpha)
                mid_col = (255, 220, 65, alpha)
                cor_col = (255, 255, 240, alpha)
                smoke_hi = None
            elif norm_t < 0.52:
                sub_t = (norm_t - 0.24) / 0.28
                alpha = int(250 - 35 * sub_t)
                rim_col = (int(215*(1-sub_t) + 75*sub_t), int(150*(1-sub_t) + 65*sub_t), int(25*(1-sub_t) + 35*sub_t), alpha)
                mid_col = (int(255*(1-sub_t) + 210*sub_t), int(220*(1-sub_t) + 160*sub_t), int(65*(1-sub_t) + 40*sub_t), alpha)
                cor_col = (int(255*(1-sub_t) + 255*sub_t), int(255*(1-sub_t) + 240*sub_t), int(240*(1-sub_t) + 140*sub_t), alpha)
                smoke_hi = None
            elif norm_t < 0.78:
                sub_t = (norm_t - 0.52) / 0.26
                alpha = int(215 * (1.0 - 0.35 * sub_t))
                rim_col = (52, 45, 32, alpha)
                mid_col = (82, 72, 48, alpha)
                smoke_hi = (118, 104, 68, alpha)
                cor_col = (245, 200, 50, int(alpha * (1.0 - sub_t)))
            else:
                sub_t = (norm_t - 0.78) / 0.22
                alpha = int(140 * (1.0 - sub_t))
                rim_col = (40, 35, 26, alpha)
                mid_col = (65, 58, 40, alpha)
                smoke_hi = (92, 82, 54, alpha)
                cor_col = None
        else:  # "fire"
            if norm_t < 0.24:
                alpha = 255
                rim_col = (235, 55, 10, alpha)
                mid_col = (255, 175, 25, alpha)
                cor_col = (255, 255, 220, alpha)
                smoke_hi = None
            elif norm_t < 0.52:
                sub_t = (norm_t - 0.24) / 0.28
                alpha = int(250 - 30 * sub_t)
                rim_col = (int(235*(1-sub_t) + 46*sub_t), int(55*(1-sub_t) + 38*sub_t), int(10*(1-sub_t) + 46*sub_t), alpha)
                mid_col = (int(255*(1-sub_t) + 185*sub_t), int(175*(1-sub_t) + 65*sub_t), int(25*(1-sub_t) + 15*sub_t), alpha)
                cor_col = (int(255*(1-sub_t) + 255*sub_t), int(255*(1-sub_t) + 145*sub_t), int(220*(1-sub_t) + 30*sub_t), alpha)
                smoke_hi = None
            elif norm_t < 0.78:
                sub_t = (norm_t - 0.52) / 0.26
                alpha = int(220 * (1.0 - 0.35 * sub_t))
                rim_col = (36, 32, 40, alpha)
                mid_col = (55, 48, 58, alpha)
                smoke_hi = (75, 68, 78, alpha)
                cor_col = (200, 65, 15, int(alpha * (1.0 - sub_t)))
            else:
                sub_t = (norm_t - 0.78) / 0.22
                alpha = int(140 * (1.0 - sub_t))
                rim_col = (28, 24, 32, alpha)
                mid_col = (46, 42, 52, alpha)
                smoke_hi = (65, 60, 70, alpha)
                cor_col = None

        if alpha > 3:
            # 1. Outer Rim Layer (Forms fluid cauliflower silhouette)
            for px, py, cur_r, is_core, (ox_sub, oy_sub) in lobe_renders:
                pygame.draw.circle(exp_surf, rim_col, (int(px), int(py)), int(cur_r))
                pygame.draw.circle(exp_surf, rim_col, (int(px + ox_sub), int(py + oy_sub)), int(cur_r * 0.78))

            # 1.5 Explosive Tendrils / Starburst Spikes
            if norm_t < 0.38:
                for sp in self.spikes:
                    if sp["ttl"] <= 0:
                        continue
                    ratio = sp["ttl"] / sp["max_ttl"]
                    dist = sp["dist"]
                    t_len = sp["len"] * ratio
                    t_w = max(2.5, sp["w"] * ratio)
                    tx = center_x + math.cos(sp["ang"]) * (dist + t_len)
                    ty = center_y + math.sin(sp["ang"]) * (dist + t_len)
                    perp = sp["ang"] + math.pi / 2.0
                    b1x = center_x + math.cos(sp["ang"]) * dist + math.cos(perp) * (t_w * 0.5)
                    b1y = center_y + math.sin(sp["ang"]) * dist + math.sin(perp) * (t_w * 0.5)
                    b2x = center_x + math.cos(sp["ang"]) * dist - math.cos(perp) * (t_w * 0.5)
                    b2y = center_y + math.sin(sp["ang"]) * dist - math.sin(perp) * (t_w * 0.5)
                    pygame.draw.polygon(exp_surf, rim_col, [(b1x, b1y), (tx, ty), (b2x, b2y)])
                    if ratio > 0.4:
                        pygame.draw.polygon(exp_surf, mid_col, [
                            (b1x*0.6 + center_x*0.4, b1y*0.6 + center_y*0.4),
                            (tx*0.8 + center_x*0.2, ty*0.8 + center_y*0.2),
                            (b2x*0.6 + center_x*0.4, b2y*0.6 + center_y*0.4)
                        ])

            # 2. Mid Layer (Body of flame or mid-tone smoke)
            for px, py, cur_r, is_core, (ox_sub, oy_sub) in lobe_renders:
                if cur_r >= 4:
                    pygame.draw.circle(exp_surf, mid_col, (int(px), int(py - cur_r * 0.12)), int(cur_r * 0.74))
                    pygame.draw.circle(exp_surf, mid_col, (int(px + ox_sub * 0.6), int(py + oy_sub * 0.6 - cur_r * 0.1)), int(cur_r * 0.55))

            # 2.5 Smoke 3D Highlights
            if smoke_hi is not None:
                for px, py, cur_r, is_core, _ in lobe_renders:
                    if cur_r >= 8:
                        pygame.draw.circle(exp_surf, smoke_hi, (int(px), int(py - cur_r * 0.3)), int(cur_r * 0.46))

            # 3. Core Layer (White-hot / glowing heart)
            if cor_col is not None:
                for px, py, cur_r, is_core, _ in lobe_renders:
                    if cur_r >= 5 and (is_core or norm_t < 0.35):
                        pygame.draw.circle(exp_surf, cor_col, (int(px), int(py - cur_r * 0.2)), max(2, int(cur_r * 0.48)))
                        if norm_t < 0.18 and cur_r >= 9:
                            pygame.draw.circle(exp_surf, (255, 255, 255, alpha), (int(px), int(py - cur_r * 0.28)), max(1, int(cur_r * 0.26)))

        target.blit(exp_surf, (int(self.x + ox - center_x), int(self.y + oy - center_y)))

        # 3. High-Velocity Motion-Blurred Tracer Sparks
        for sp in self.sparks:
            if sp["ttl"] <= 0:
                continue
            ratio = sp["ttl"] / sp["max_ttl"]
            if ratio > 0.60:
                col = self.spark_head
            elif ratio > 0.30:
                col = self.spark_mid
            else:
                col = self.spark_tail

            head_x = sp["x"] + ox
            head_y = sp["y"] + oy
            tail_x = head_x - sp["vx"] * sp["streak"]
            tail_y = head_y - sp["vy"] * sp["streak"]

            pygame.draw.line(target, col, (int(tail_x), int(tail_y)), (int(head_x), int(head_y)), max(1, sp["size"]))
            head_sz = max(1, int(sp["size"] * (0.6 + 0.4 * ratio)))
            pygame.draw.circle(target, (255, 255, 255), (int(head_x), int(head_y)), head_sz)

        # 4. Tumbling Shrapnel Debris
        for db in self.debris:
            if db["ttl"] <= 0:
                continue
            ratio = db["ttl"] / db["max_ttl"]
            dsz = max(2.5, db["size"] * (0.6 + 0.4 * ratio))
            dx, dy = int(db["x"] + ox), int(db["y"] + oy)

            rad_ang = math.radians(db["rot"])
            cos_a = math.cos(rad_ang) * dsz
            sin_a = math.sin(rad_ang) * dsz
            pts = [
                (dx + cos_a, dy + sin_a),
                (dx - sin_a * 1.1, dy + cos_a * 0.9),
                (dx - cos_a, dy - sin_a),
                (dx + sin_a * 0.7, dy - cos_a * 0.8)
            ]
            pygame.draw.polygon(target, self.debris_col, pts)
            pygame.draw.polygon(target, self.debris_hi, [(p[0] - 0.7, p[1] - 0.7) for p in pts[:3]])


class ParticleSystem:
    """Advanced procedural pixel-art FX system: fluid multi-frame explosions, incandescent sparks, shrapnel & combat text."""

    def __init__(self) -> None:
        self.explosions: List[FluidExplosion] = []
        self.particles: List[Dict[str, Any]] = []
        self.floating_texts: List[Dict[str, Any]] = []
        # Maintained for backwards compatibility
        self.shockwaves: List[Dict[str, Any]] = []
        self.fireballs: List[Dict[str, Any]] = []

    def clear(self) -> None:
        self.explosions.clear()
        self.particles.clear()
        self.floating_texts.clear()
        self.shockwaves.clear()
        self.fireballs.clear()

    # ------------------------------------------------------------------
    # HIT SPARKS (WEAPON IMPACTS)
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
    # FLUID PROCEDURAL EXPLOSIONS (ARTILLERY, METEOR, CASTLE BREACH)
    # ------------------------------------------------------------------
    def spawn_explosion(
        self,
        pos: Tuple[float, float],
        radius: float = 65.0,
        kind: str = "fire",
    ) -> None:
        """Spawns an authentic procedural fluid explosion with supersonic shockwaves,
        cauliflower roiling fireball, high-velocity motion-blurred tracer sparks, and buoyant smoke."""
        self.explosions.append(FluidExplosion(pos[0], pos[1], radius=radius, kind=kind))

    # ------------------------------------------------------------------
    # FROST NOVA
    # ------------------------------------------------------------------
    def spawn_frost_nova(self, pos: Tuple[float, float], radius: float = 55.0) -> None:
        self.spawn_explosion(pos, radius, kind="frost")

    # ------------------------------------------------------------------
    # HOLY BURST (SIR ROLAND'S HOLY JUDGMENT)
    # ------------------------------------------------------------------
    def spawn_holy_burst(self, pos: Tuple[float, float], radius: float = 85.0) -> None:
        self.spawn_explosion(pos, radius, kind="holy")

    # ------------------------------------------------------------------
    # BUILDING / UPGRADE SPARKLES
    # ------------------------------------------------------------------
    def spawn_build_sparkles(self, pos: Tuple[float, float], color: Tuple[int, int, int] = pal.GOLD_SHINE) -> None:
        x, y = float(pos[0]), float(pos[1])
        for _ in range(16):
            ang = random.uniform(0.0, math.tau)
            spd = random.uniform(40.0, 120.0)
            self.particles.append({
                "x": x + random.uniform(-10.0, 10.0),
                "y": y + random.uniform(-10.0, 10.0),
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

        # Update fluid explosions
        for exp in list(self.explosions):
            exp.update(dt_ms)
            if not exp.alive:
                self.explosions.remove(exp)

        # Update basic particles (hit sparks & upgrade sparkles)
        for p in list(self.particles):
            p["ttl"] -= dt_ms
            if p["ttl"] <= 0:
                self.particles.remove(p)
                continue
            p["vy"] += p.get("gravity", 0.0) * dt_s
            p["x"] += p["vx"] * dt_s
            p["y"] += p["vy"] * dt_s

        # Update floating texts
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

        # 1. Fluid Explosions (shockwaves, roiling fireball/smoke, tracer sparks, shrapnel)
        for exp in self.explosions:
            exp.draw(surface, ox, oy)

        # 2. Crisp square pixel particles & hit sparks
        for p in self.particles:
            ratio = max(0.2, p["ttl"] / p["max_ttl"])
            sz = max(2, int(p["size"] * ratio))
            px = int(p["x"] + ox) - sz // 2
            py = int(p["y"] + oy) - sz // 2
            if p.get("outline", False):
                pygame.draw.rect(surface, pal.OUTLINE_DARK, (px - 1, py - 1, sz + 2, sz + 2))
            pygame.draw.rect(surface, p["color"], (px, py, sz, sz))

        # 3. Floating Combat Text
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
