from __future__ import annotations
import math
from typing import Dict, List, Tuple, Any
import pygame


Color = Tuple[int, int, int]


def _lerp_color(c1: Color, c2: Color, t: float) -> Color:
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


class LightingEngine:
    """Real-time 2D dynamic lighting, day/night cycle, and additive bloom pipeline."""

    MODES = ["auto", "day", "dusk", "night"]
    MODE_LABELS = {
        "auto": "Auto Cycle",
        "day": "Daylight",
        "dusk": "Sunset",
        "night": "Night",
    }

    # Ambient light colors for multiplicative pass (255,255,255 = full brightness)
    AMBIENT_DAY: Color = (255, 252, 245)
    AMBIENT_DUSK: Color = (205, 148, 165)
    AMBIENT_NIGHT: Color = (68, 78, 132)

    def __init__(self, width: int, height: int, scale_div: int = 4) -> None:
        self.width = width
        self.height = height
        self.scale_div = max(2, int(scale_div))
        self.lw = max(80, width // self.scale_div)
        self.lh = max(45, height // self.scale_div)

        self.lightmap = pygame.Surface((self.lw, self.lh))
        self.bloom_map = pygame.Surface((self.lw, self.lh))
        self._brush_cache: Dict[Tuple[int, Color], pygame.Surface] = {}

        self.mode_index: int = 0
        self.time_sec: float = 0.0
        self.current_ambient: Color = self.AMBIENT_DAY
        self.darkness_factor: float = 0.0  # 0.0 = bright day, 1.0 = full night

    @property
    def mode(self) -> str:
        return self.MODES[self.mode_index % len(self.MODES)]

    @property
    def mode_label(self) -> str:
        return self.MODE_LABELS[self.mode]

    def cycle_mode(self) -> str:
        self.mode_index = (self.mode_index + 1) % len(self.MODES)
        return self.mode

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.lw = max(80, width // self.scale_div)
        self.lh = max(45, height // self.scale_div)
        self.lightmap = pygame.Surface((self.lw, self.lh))
        self.bloom_map = pygame.Surface((self.lw, self.lh))
        self._brush_cache.clear()

    def _get_brush(self, radius_lowres: int, color: Color) -> pygame.Surface:
        r = max(4, min(160, int(radius_lowres)))
        # Quantize color slightly to keep brush cache small and fast
        q_col: Color = (
            min(255, (color[0] // 8) * 8),
            min(255, (color[1] // 8) * 8),
            min(255, (color[2] // 8) * 8),
        )
        key = (r, q_col)
        if key in self._brush_cache:
            return self._brush_cache[key]

        diam = r * 2
        surf = pygame.Surface((diam, diam))
        surf.fill((0, 0, 0))
        steps = max(8, min(22, r))
        for i in range(steps, 0, -1):
            p = i / float(steps)
            # Smooth quadratic falloff from center to edge
            intensity = (1.0 - p) ** 1.65
            cr = int(q_col[0] * intensity)
            cg = int(q_col[1] * intensity)
            cb = int(q_col[2] * intensity)
            pygame.draw.circle(surf, (cr, cg, cb), (r, r), int(r * p))

        self._brush_cache[key] = surf
        return surf

    def update(self, dt_ms: float, current_wave: int) -> None:
        self.time_sec += dt_ms / 1000.0
        m = self.mode

        target_amb = self.AMBIENT_DAY
        target_dark = 0.05

        if m == "day":
            target_amb = self.AMBIENT_DAY
            target_dark = 0.05
        elif m == "dusk":
            target_amb = self.AMBIENT_DUSK
            target_dark = 0.55
        elif m == "night":
            target_amb = self.AMBIENT_NIGHT
            target_dark = 1.0
        else:
            # Auto cycle based on wave progression + gentle time breathing
            w_mod = (max(1, current_wave) - 1) % 6
            if w_mod in (0, 1):
                # Waves 1-2: Daylight -> Late Afternoon
                target_amb = _lerp_color(self.AMBIENT_DAY, self.AMBIENT_DUSK, 0.25 * w_mod)
                target_dark = 0.08 + 0.15 * w_mod
            elif w_mod == 2:
                # Wave 3: Sunset Dusk
                target_amb = self.AMBIENT_DUSK
                target_dark = 0.58
            elif w_mod in (3, 4):
                # Waves 4-5 (Boss wave!): Starlit Night
                target_amb = self.AMBIENT_NIGHT
                target_dark = 0.95
            else:
                # Wave 6: Dawn transition
                target_amb = _lerp_color(self.AMBIENT_NIGHT, self.AMBIENT_DUSK, 0.65)
                target_dark = 0.45

        lerp_spd = min(1.0, (dt_ms / 1000.0) * 2.5)
        self.current_ambient = _lerp_color(self.current_ambient, target_amb, lerp_spd)
        self.darkness_factor += (target_dark - self.darkness_factor) * lerp_spd

    def render_lighting(
        self,
        target_surface: pygame.Surface,
        game_scene: Any,
        world_fx: Any = None,
    ) -> None:
        """Collects all active scene lights and composites multiplicative lightmap + additive bloom."""
        ox, oy = game_scene.camera_offset
        s = game_scene.ui_scale
        div = float(self.scale_div)

        self.lightmap.fill(self.current_ambient)
        self.bloom_map.fill((0, 0, 0))

        pulse = 0.92 + 0.08 * math.sin(self.time_sec * 5.5)
        flicker = 0.94 + 0.06 * math.sin(self.time_sec * 17.0)

        def add_light(
            wx: float,
            wy: float,
            radius_px: float,
            color: Color,
            bloom_intensity: float = 0.35,
        ) -> None:
            lx = int((wx + ox) / div)
            ly = int((wy + oy) / div)
            lr = int((radius_px / div))
            if lr < 3:
                return
            brush = self._get_brush(lr, color)
            self.lightmap.blit(brush, (lx - lr, ly - lr), special_flags=pygame.BLEND_RGB_ADD)
            if bloom_intensity > 0.02:
                b_col: Color = (
                    int(color[0] * bloom_intensity),
                    int(color[1] * bloom_intensity),
                    int(color[2] * bloom_intensity),
                )
                b_brush = self._get_brush(max(4, int(lr * 0.78)), b_col)
                self.bloom_map.blit(b_brush, (lx - b_brush.get_width() // 2, ly - b_brush.get_height() // 2), special_flags=pygame.BLEND_RGB_ADD)

        # 1. Dark Entrance Portal (Left) — Arcane Violet Glow
        add_light(
            game_scene.width * 0.025,
            game_scene.height * 0.30,
            115.0 * s * pulse,
            (185, 95, 255),
            bloom_intensity=0.45,
        )

        # 2. Royal Castle Twin Torches & Gate (Right)
        cx, cy = game_scene.road.castle_pos
        add_light(cx - 28 * s, cy + 4 * s, 110.0 * s * flicker, (255, 190, 95), bloom_intensity=0.35)
        add_light(cx + 28 * s, cy + 4 * s, 110.0 * s * flicker, (255, 190, 95), bloom_intensity=0.35)
        add_light(cx, cy + 16 * s, 85.0 * s, (255, 160, 70), bloom_intensity=0.22)

        # 3. Towers & Empty Slot Rune Glow
        for sl in game_scene.road.slots:
            sx, sy = sl.pos
            if sl.tower is None:
                if sl == game_scene.hovered_slot or game_scene.radial_menu.active_slot == sl:
                    add_light(sx, sy, 68.0 * s, (240, 200, 90), bloom_intensity=0.25)
                elif self.darkness_factor > 0.35:
                    add_light(sx, sy, 42.0 * s, (80, 95, 130), bloom_intensity=0.05)
            else:
                tw = sl.tower
                lvl_mult = 0.85 + 0.18 * tw.level
                if tw.tower_type == "archer":
                    add_light(sx, sy - 8 * s, 95.0 * s * lvl_mult * flicker, (245, 195, 105), bloom_intensity=0.22)
                elif tw.tower_type == "artillery":
                    col = (255, 145, 65) if tw.recoil_ms <= 0 else (255, 230, 140)
                    rad = (105.0 if tw.recoil_ms <= 0 else 145.0) * s * lvl_mult
                    add_light(sx, sy - 10 * s, rad, col, bloom_intensity=0.32 if tw.recoil_ms <= 0 else 0.55)
                elif tw.tower_type == "frost":
                    add_light(sx, sy - 12 * s, 115.0 * s * lvl_mult * pulse, (95, 215, 255), bloom_intensity=0.45)
                elif tw.tower_type == "lightning":
                    add_light(sx, sy - 12 * s, 122.0 * s * lvl_mult * pulse, (195, 115, 255), bloom_intensity=0.50)

        # 4. Boss Magma Core & Burning / Slowed Enemies
        for e in game_scene.enemies:
            if not e.alive:
                continue
            if e.boss:
                add_light(e.x, e.y - 6 * s, 110.0 * s * pulse, (255, 120, 45), bloom_intensity=0.45)
            elif e.burn_timer_ms > 0:
                add_light(e.x, e.y, 55.0 * s * flicker, (255, 130, 40), bloom_intensity=0.30)

        # 5. Active Projectiles, Chain Lightning Arcs & Falling Meteors
        for proj in game_scene.projectiles:
            if not proj.active:
                continue
            py_vis = proj.y - proj.z_height
            if proj.kind == "bomb":
                add_light(proj.x, py_vis, 68.0 * s, (255, 165, 65), bloom_intensity=0.38)
            elif proj.kind == "frost":
                add_light(proj.x, py_vis, 62.0 * s, (110, 225, 255), bloom_intensity=0.40)
            else:
                add_light(proj.x, py_vis, 38.0 * s, (220, 235, 175), bloom_intensity=0.15)

        for arc in game_scene.lightning_arcs:
            for seg in arc.segments:
                for pt in seg[::2]:
                    add_light(pt[0], pt[1], 72.0 * s, (215, 150, 255), bloom_intensity=0.55)

        for m in game_scene.falling_meteors:
            if m["delay_ms"] <= 0:
                p = min(1.0, m["progress"])
                mx_p = m["x"] + (m["tx"] - m["x"]) * p
                my_p = m["y"] + (m["ty"] - m["y"]) * p
                add_light(mx_p, my_p, 135.0 * s, (255, 145, 50), bloom_intensity=0.65)

        for sw in game_scene.particles.shockwaves:
            p = sw["ttl"] / max(1.0, sw["max_ttl"])
            add_light(sw["x"], sw["y"], sw["max_r"] * 1.4 * p, sw["color"], bloom_intensity=0.55 * p)

        # 6. Ambient Fireflies (from WorldEffectsSystem)
        if world_fx is not None:
            for ff in world_fx.fireflies:
                glow = 0.5 + 0.5 * math.sin(ff["phase"])
                if glow > 0.2:
                    add_light(
                        ff["x"],
                        ff["y"],
                        34.0 * s * glow,
                        ff["color"],
                        bloom_intensity=0.35 * glow,
                    )

        # Composite Multiplicative Lightmap (when dusk/night or subtle daylight shading)
        if self.darkness_factor > 0.03:
            scaled_light = pygame.transform.smoothscale(self.lightmap, (self.width, self.height))
            target_surface.blit(scaled_light, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Composite Additive Bloom Pass (always active, stronger at dusk/night)
        scaled_bloom = pygame.transform.smoothscale(self.bloom_map, (self.width, self.height))
        target_surface.blit(scaled_bloom, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
