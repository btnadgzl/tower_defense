from __future__ import annotations
import math
from typing import Dict, Tuple
import pygame
from graphics import palette as pal


def apply_pixel_outline(
    surf: pygame.Surface,
    outline_color: Tuple[int, int, int] = pal.OUTLINE_DARK,
) -> pygame.Surface:
    """Adds a crisp 1px pixel-art contour around all non-transparent pixels."""
    w, h = surf.get_size()
    out = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(surf, 10)
    # Blit 4-neighbor silhouette for clean pixel-art outline
    silhouette = mask.to_surface(setcolor=(*outline_color, 255), unsetcolor=(0, 0, 0, 0))
    out.blit(silhouette, (0, 1))
    out.blit(silhouette, (2, 1))
    out.blit(silhouette, (1, 0))
    out.blit(silhouette, (1, 2))
    out.blit(surf, (1, 1))
    return out


def tint_surface(
    surf: pygame.Surface,
    tint_rgb: Tuple[int, int, int],
    strength: float = 0.5,
) -> pygame.Surface:
    """Applies a pixel-preserving color tint (for hit flash or frost slow)."""
    res = surf.copy()
    overlay = pygame.Surface(res.get_size(), pygame.SRCALPHA)
    r, g, b = tint_rgb
    a = int(max(0, min(255, 255 * strength)))
    overlay.fill((r, g, b, a))
    res.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    if strength > 0.65:
        add_srf = pygame.Surface(res.get_size(), pygame.SRCALPHA)
        mask = pygame.mask.from_surface(surf, 10)
        white_sil = mask.to_surface(setcolor=(r, g, b, 140), unsetcolor=(0, 0, 0, 0))
        add_srf.blit(white_sil, (0, 0))
        res.blit(add_srf, (0, 0))
    return res


def upscale_pixel(surf: pygame.Surface, scale: int) -> pygame.Surface:
    if scale <= 1:
        return surf
    w, h = surf.get_size()
    return pygame.transform.scale(surf, (w * scale, h * scale))


class PixelArtGenerator:
    """Generates and caches all procedural pixel-art sprites, towers, enemies, heroes, and icons."""

    def __init__(self, pixel_scale: int = 3) -> None:
        self.pixel_scale = max(1, int(pixel_scale))
        self._cache: Dict[Tuple, pygame.Surface] = {}

    def clear_cache(self, new_scale: int | None = None) -> None:
        if new_scale is not None:
            self.pixel_scale = max(1, int(new_scale))
        self._cache.clear()

    # ------------------------------------------------------------------
    # TACTICAL BUILD SLOT PAD
    # ------------------------------------------------------------------
    def get_slot_pad(self, hovered: bool = False, selected: bool = False) -> pygame.Surface:
        key = ("slot_pad", hovered, selected, self.pixel_scale)
        if key in self._cache:
            return self._cache[key]

        s = pygame.Surface((22, 18), pygame.SRCALPHA)
        border_col = pal.GOLD_LIGHT if (hovered or selected) else pal.STONE_DARK
        fill_col = pal.STONE_LIGHT if hovered else pal.STONE_MID
        pygame.draw.ellipse(s, border_col, (1, 2, 20, 14))
        pygame.draw.ellipse(s, fill_col, (2, 3, 18, 12))
        pygame.draw.ellipse(s, pal.STONE_DARK, (4, 5, 14, 8), 1)
        for px, py in [(4, 5), (17, 5), (4, 11), (17, 11)]:
            s.set_at((px, py), pal.STONE_HIGHLIGHT)
        rune_col = pal.GOLD_SHINE if (hovered or selected) else pal.STONE_HIGHLIGHT
        pygame.draw.line(s, rune_col, (9, 8), (12, 8))
        pygame.draw.line(s, rune_col, (10, 6), (10, 10))

        outlined = apply_pixel_outline(s)
        res = upscale_pixel(outlined, self.pixel_scale)
        self._cache[key] = res
        return res

    # ------------------------------------------------------------------
    # TOWER BASE & TURRET SPRITES (4 ARCHETYPES x 3 LEVELS)
    # ------------------------------------------------------------------
    def get_tower_base(self, tower_type: str, level: int) -> pygame.Surface:
        key = ("tower_base", tower_type, level, self.pixel_scale)
        if key in self._cache:
            return self._cache[key]

        s = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(s, pal.STONE_DARK, (2, 12, 20, 10))
        pygame.draw.ellipse(s, pal.STONE_MID, (3, 11, 18, 9))

        if tower_type == "archer":
            w_col = pal.WOOD_MID if level < 3 else pal.WOOD_DARK
            w_hi = pal.WOOD_LIGHT if level < 3 else pal.GOLD_MID
            pygame.draw.rect(s, pal.WOOD_DARK, (5, 7, 14, 11))
            pygame.draw.rect(s, w_col, (6, 7, 12, 10))
            pygame.draw.line(s, w_hi, (7, 7), (7, 16))
            pygame.draw.line(s, w_hi, (16, 7), (16, 16))
            pygame.draw.rect(s, pal.STONE_LIGHT if level >= 2 else pal.WOOD_LIGHT, (4, 5, 16, 3))
            if level >= 2:
                pygame.draw.rect(s, pal.ARCHER_GREEN_MID, (10, 10, 4, 6))
                s.set_at((11, 11), pal.GOLD_LIGHT)
            if level >= 3:
                for bx in (4, 9, 14, 18):
                    pygame.draw.rect(s, pal.GOLD_MID, (bx, 4, 2, 2))

        elif tower_type == "artillery":
            pygame.draw.rect(s, pal.STONE_DARK, (4, 8, 16, 10))
            pygame.draw.rect(s, pal.STONE_MID, (5, 8, 14, 9))
            pygame.draw.rect(s, pal.IRON_DARK, (3, 6, 18, 3))
            pygame.draw.rect(s, pal.IRON_MID, (4, 6, 16, 2))
            if level >= 2:
                for rx in (6, 10, 14, 17):
                    s.set_at((rx, 11), pal.IRON_SPECULAR)
            if level >= 3:
                pygame.draw.rect(s, pal.GOLD_MID, (4, 13, 16, 2))
                pygame.draw.rect(s, pal.FIRE_MID, (9, 10, 6, 3))

        elif tower_type == "frost":
            pygame.draw.polygon(s, pal.STONE_LIGHT, [(6, 18), (18, 18), (16, 6), (8, 6)])
            pygame.draw.polygon(s, pal.STONE_HIGHLIGHT, [(7, 17), (12, 17), (11, 6), (8, 6)])
            pygame.draw.rect(s, pal.FROST_DARK, (9, 9, 6, 7))
            pygame.draw.rect(s, pal.FROST_LIGHT, (10, 10, 4, 5))
            if level >= 2:
                pygame.draw.polygon(s, pal.FROST_MID, [(3, 16), (6, 10), (6, 17)])
                pygame.draw.polygon(s, pal.FROST_MID, [(20, 16), (17, 10), (17, 17)])
            if level >= 3:
                pygame.draw.rect(s, pal.GOLD_MID, (7, 5, 10, 2))

        elif tower_type == "lightning":
            pygame.draw.polygon(s, pal.UI_BG_MID, [(5, 18), (19, 18), (17, 6), (7, 6)])
            pygame.draw.polygon(s, pal.UI_BG_LIGHT, [(6, 17), (12, 17), (11, 6), (8, 6)])
            pygame.draw.line(s, pal.ARCANE_MID, (11, 8), (11, 16), 2)
            pygame.draw.line(s, pal.ARCANE_CORE, (11, 9), (11, 15), 1)
            if level >= 2:
                pygame.draw.rect(s, pal.GOLD_MID, (6, 6, 12, 2))
            if level >= 3:
                pygame.draw.rect(s, pal.GOLD_LIGHT, (5, 15, 14, 2))
                s.set_at((8, 11), pal.ARCANE_LIGHT)
                s.set_at((15, 11), pal.ARCANE_LIGHT)

        outlined = apply_pixel_outline(s)
        res = upscale_pixel(outlined, self.pixel_scale)
        self._cache[key] = res
        return res

    def get_tower_turret(
        self,
        tower_type: str,
        level: int,
        angle_deg: float,
        anim_step: int = 0,
    ) -> pygame.Surface:
        q_angle = int(round(angle_deg / 15.0) * 15) % 360
        step = anim_step % 4
        key = ("tower_turret", tower_type, level, q_angle, step, self.pixel_scale)
        if key in self._cache:
            return self._cache[key]

        s = pygame.Surface((22, 22), pygame.SRCALPHA)
        cx, cy = 11, 11

        if tower_type == "archer":
            hood_col = pal.ARCHER_GREEN_MID if level < 3 else pal.CRIMSON_LIGHT
            pygame.draw.circle(s, hood_col, (cx - 1, cy), 4)
            pygame.draw.circle(s, pal.ARCHER_GREEN_LIGHT if level < 3 else pal.GOLD_LIGHT, (cx - 2, cy - 1), 2)
            bow_col = pal.WOOD_LIGHT if level == 1 else (pal.IRON_LIGHT if level == 2 else pal.GOLD_LIGHT)
            pygame.draw.line(s, bow_col, (cx + 3, cy - 6), (cx + 6, cy), 2)
            pygame.draw.line(s, bow_col, (cx + 3, cy + 6), (cx + 6, cy), 2)
            pygame.draw.line(s, pal.STONE_HIGHLIGHT, (cx + 3, cy - 5), (cx + 3, cy + 5), 1)
            pygame.draw.line(s, pal.WOOD_HIGHLIGHT, (cx, cy), (cx + 8, cy), 2)
            s.set_at((cx + 9, cy), pal.IRON_SPECULAR)
            if level >= 3:
                pygame.draw.line(s, pal.GOLD_SHINE, (cx, cy - 2), (cx + 8, cy - 2), 1)
                pygame.draw.line(s, pal.GOLD_SHINE, (cx, cy + 2), (cx + 8, cy + 2), 1)
            rot = pygame.transform.rotate(s, -q_angle)
            rw, rh = rot.get_size()
            cropped = pygame.Surface((22, 22), pygame.SRCALPHA)
            cropped.blit(rot, ((22 - rw) // 2, (22 - rh) // 2))
            s = cropped

        elif tower_type == "artillery":
            barrel_col = pal.IRON_MID if level < 3 else pal.IRON_DARK
            trim_col = pal.IRON_LIGHT if level == 1 else (pal.GOLD_MID if level == 2 else pal.GOLD_LIGHT)
            pygame.draw.circle(s, pal.IRON_DARK, (cx - 1, cy), 6)
            pygame.draw.rect(s, barrel_col, (cx - 2, cy - 4, 11, 8))
            pygame.draw.rect(s, pal.IRON_LIGHT, (cx - 1, cy - 3, 9, 2))
            pygame.draw.rect(s, trim_col, (cx + 7, cy - 5, 3, 10))
            if level >= 2:
                pygame.draw.rect(s, trim_col, (cx, cy - 5, 2, 10))
            if level >= 3:
                pygame.draw.circle(s, pal.FIRE_LIGHT, (cx - 2, cy), 2)
            rot = pygame.transform.rotate(s, -q_angle)
            rw, rh = rot.get_size()
            cropped = pygame.Surface((22, 22), pygame.SRCALPHA)
            cropped.blit(rot, ((22 - rw) // 2, (22 - rh) // 2))
            s = cropped

        elif tower_type == "frost":
            bob = -1 if step in (1, 2) else 0
            pts = [(cx, 2 + bob), (cx + 5, cy + bob), (cx, 17 + bob), (cx - 5, cy + bob)]
            pygame.draw.polygon(s, pal.FROST_MID, pts)
            pygame.draw.polygon(s, pal.FROST_LIGHT, [(cx, 2 + bob), (cx - 5, cy + bob), (cx, cy + bob)])
            pygame.draw.polygon(s, pal.FROST_CORE, [(cx, 4 + bob), (cx - 2, cy - 1 + bob), (cx, cy + 2 + bob)])
            shard_count = level + 1
            for i in range(shard_count):
                ang = math.radians(step * 45 + i * (360 // shard_count))
                ox = int(cx + math.cos(ang) * 8)
                oy = int(cy + math.sin(ang) * 5) + bob
                pygame.draw.rect(s, pal.FROST_CORE, (ox - 1, oy - 1, 3, 3))

        elif tower_type == "lightning":
            bob = -1 if step in (1, 2) else 0
            pygame.draw.polygon(s, pal.GOLD_MID, [(cx - 6, 14), (cx - 4, 5), (cx - 2, 14)])
            pygame.draw.polygon(s, pal.GOLD_MID, [(cx + 6, 14), (cx + 4, 5), (cx + 2, 14)])
            orb_r = 4 + (1 if level >= 3 else 0)
            pygame.draw.circle(s, pal.ARCANE_DARK, (cx, 8 + bob), orb_r + 1)
            pygame.draw.circle(s, pal.ARCANE_MID, (cx, 8 + bob), orb_r)
            pygame.draw.circle(s, pal.ARCANE_CORE, (cx - 1, 7 + bob), max(2, orb_r - 2))
            spark_offsets = [(-5, 4), (5, 4), (0, 2), (-4, 10)][step]
            s.set_at((cx + spark_offsets[0], 8 + bob + spark_offsets[1] // 2), pal.ARCANE_CORE)

        outlined = apply_pixel_outline(s)
        res = upscale_pixel(outlined, self.pixel_scale)
        self._cache[key] = res
        return res

    # ------------------------------------------------------------------
    # ROYAL PALADIN HERO SPRITE
    # ------------------------------------------------------------------
    def get_hero_sprite(
        self,
        walk_frame: int = 0,
        attack_frame: int = 0,
        hit_flash: bool = False,
        facing_left: bool = False,
        level: int = 1,
    ) -> pygame.Surface:
        f = walk_frame % 4
        atk = attack_frame % 3
        key = ("hero_paladin", f, atk, hit_flash, facing_left, level, self.pixel_scale)
        if key in self._cache:
            return self._cache[key]

        s = pygame.Surface((26, 26), pygame.SRCALPHA)
        bob = -1 if f in (1, 3) else 0
        l_off = -2 if f == 1 else (2 if f == 3 else 0)

        # Fluttering Royal Blue & Gold Cape
        cape_col = pal.ROYAL_BLUE_LIGHT if level >= 3 else pal.ROYAL_BLUE_DARK
        pygame.draw.polygon(s, cape_col, [(4, 8 + bob), (9, 8 + bob), (7, 20), (2 - (f % 2), 19)])
        pygame.draw.line(s, pal.GOLD_LIGHT, (3, 19), (7, 20), 1)

        # Greaves & Sabatons
        pygame.draw.rect(s, pal.IRON_LIGHT, (8 + l_off, 18, 3, 5))
        pygame.draw.rect(s, pal.IRON_LIGHT, (13 - l_off, 18, 3, 5))
        pygame.draw.rect(s, pal.GOLD_MID, (8 + l_off, 21, 3, 2))
        pygame.draw.rect(s, pal.GOLD_MID, (13 - l_off, 21, 3, 2))

        # Silver-Gold Paladin Cuirass & Tabard
        pygame.draw.rect(s, pal.IRON_SPECULAR, (7, 9 + bob, 9, 9))
        pygame.draw.rect(s, pal.ROYAL_BLUE_LIGHT, (9, 10 + bob, 5, 8))
        pygame.draw.line(s, pal.GOLD_SHINE, (11, 10 + bob), (11, 17 + bob), 1)
        pygame.draw.line(s, pal.GOLD_SHINE, (9, 13 + bob), (13, 13 + bob), 1)

        # Golden Pauldrons
        pygame.draw.circle(s, pal.GOLD_LIGHT, (7, 10 + bob), 3)
        pygame.draw.circle(s, pal.GOLD_LIGHT, (16, 10 + bob), 3)

        # Paladin Greathelm & Golden Crown / Plume
        pygame.draw.rect(s, pal.IRON_SPECULAR, (8, 3 + bob, 7, 6))
        pygame.draw.line(s, pal.GOLD_MID, (8, 5 + bob), (14, 5 + bob), 1)
        pygame.draw.line(s, pal.UI_CYAN, (10, 6 + bob), (13, 6 + bob), 1)
        # Crown crest & plume
        pygame.draw.polygon(s, pal.GOLD_SHINE, [(8, 3 + bob), (11, 1 + bob), (14, 3 + bob)])
        if level >= 2:
            pygame.draw.polygon(s, pal.UI_TEXT_WHITE, [(5, 2 + bob), (9, 0 + bob), (8, 4 + bob)])

        # Aegis Kite Shield (left hand)
        pygame.draw.rect(s, pal.GOLD_MID, (5, 10 + bob, 5, 7))
        pygame.draw.rect(s, pal.ROYAL_BLUE_DARK, (6, 11 + bob, 3, 5))
        s.set_at((7, 13 + bob), pal.GOLD_SHINE)

        # Sunblade Broadsword (right hand, animated swing)
        blade_col = pal.GOLD_SHINE if level >= 4 else pal.IRON_SPECULAR
        if atk == 0:
            # Raised ready stance
            pygame.draw.line(s, pal.GOLD_MID, (16, 13 + bob), (20, 13 + bob), 2)
            pygame.draw.line(s, blade_col, (18, 13 + bob), (22, 3 + bob), 2)
            s.set_at((22, 3 + bob), pal.UI_TEXT_WHITE)
        elif atk == 1:
            # Forward cleave slash + golden arc
            pygame.draw.line(s, blade_col, (16, 11 + bob), (25, 11 + bob), 3)
            pygame.draw.arc(s, pal.GOLD_SHINE, (14, 4 + bob, 11, 14), -0.8, 0.8, 2)
        else:
            # Low follow-through
            pygame.draw.line(s, blade_col, (16, 13 + bob), (24, 18 + bob), 2)

        if facing_left:
            s = pygame.transform.flip(s, True, False)

        outlined = apply_pixel_outline(s)
        if hit_flash:
            outlined = tint_surface(outlined, (255, 255, 255), 0.80)

        res = upscale_pixel(outlined, self.pixel_scale)
        self._cache[key] = res
        return res

    # ------------------------------------------------------------------
    # 5 ENEMY ARCHETYPES x 4 WALK FRAMES
    # ------------------------------------------------------------------
    def get_enemy_sprite(
        self,
        enemy_type: str,
        walk_frame: int = 0,
        hit_flash: bool = False,
        slowed: bool = False,
        facing_left: bool = False,
    ) -> pygame.Surface:
        f = walk_frame % 4
        key = ("enemy", enemy_type, f, hit_flash, slowed, facing_left, self.pixel_scale)
        if key in self._cache:
            return self._cache[key]

        if enemy_type == "boss_golem":
            s = self._draw_boss_golem(f)
        elif enemy_type == "knight":
            s = self._draw_knight(f)
        elif enemy_type == "orc":
            s = self._draw_orc(f)
        elif enemy_type == "warg":
            s = self._draw_warg(f)
        else:
            s = self._draw_goblin(f)

        if facing_left:
            s = pygame.transform.flip(s, True, False)

        outlined = apply_pixel_outline(s)
        if slowed:
            outlined = tint_surface(outlined, (110, 200, 255), 0.45)
        if hit_flash:
            outlined = tint_surface(outlined, (255, 255, 255), 0.80)

        res = upscale_pixel(outlined, self.pixel_scale)
        self._cache[key] = res
        return res

    def _draw_goblin(self, f: int) -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        bob = -1 if f in (1, 3) else 0
        l_off = -2 if f == 1 else (2 if f == 3 else 0)
        pygame.draw.rect(s, pal.WOOD_DARK, (5 + l_off, 12, 2, 3))
        pygame.draw.rect(s, pal.WOOD_DARK, (9 - l_off, 12, 2, 3))
        pygame.draw.rect(s, pal.WOOD_MID, (5, 7 + bob, 6, 5))
        pygame.draw.rect(s, pal.GOBLIN_SKIN_LIGHT, (5, 3 + bob, 6, 4))
        pygame.draw.polygon(s, pal.GOBLIN_SKIN_DARK, [(2, 4 + bob), (5, 4 + bob), (5, 6 + bob)])
        pygame.draw.polygon(s, pal.GOBLIN_SKIN_DARK, [(13, 4 + bob), (11, 4 + bob), (11, 6 + bob)])
        s.set_at((9, 4 + bob), pal.FIRE_LIGHT)
        pygame.draw.line(s, pal.IRON_SPECULAR, (11, 8 + bob), (14, 6 + bob + (1 if f % 2 else 0)), 2)
        return s

    def _draw_orc(self, f: int) -> pygame.Surface:
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        bob = -1 if f in (1, 3) else 0
        l_off = -2 if f == 1 else (2 if f == 3 else 0)
        pygame.draw.rect(s, pal.WOOD_DARK, (6 + l_off, 15, 3, 4))
        pygame.draw.rect(s, pal.WOOD_DARK, (11 - l_off, 15, 3, 4))
        pygame.draw.rect(s, pal.ORC_SKIN_DARK, (5, 7 + bob, 10, 8))
        pygame.draw.rect(s, pal.ORC_SKIN_LIGHT, (6, 7 + bob, 8, 6))
        pygame.draw.rect(s, pal.WOOD_MID, (5, 13 + bob, 10, 2))
        pygame.draw.rect(s, pal.GOLD_MID, (9, 13 + bob, 2, 2))
        pygame.draw.circle(s, pal.IRON_MID, (6, 8 + bob), 3)
        pygame.draw.rect(s, pal.ORC_SKIN_LIGHT, (7, 2 + bob, 6, 5))
        s.set_at((11, 4 + bob), pal.FIRE_MID)
        s.set_at((12, 6 + bob), pal.STONE_HIGHLIGHT)
        axe_y = 5 + bob + (1 if f in (2, 3) else 0)
        pygame.draw.line(s, pal.WOOD_LIGHT, (14, 12 + bob), (15, axe_y), 2)
        pygame.draw.polygon(s, pal.IRON_LIGHT, [(15, axe_y), (18, axe_y - 2), (18, axe_y + 3)])
        return s

    def _draw_warg(self, f: int) -> pygame.Surface:
        s = pygame.Surface((22, 16), pygame.SRCALPHA)
        bob = -1 if f in (1, 2) else 0
        stretch = 2 if f in (1, 3) else -1
        pygame.draw.line(s, pal.UI_BG_MID, (5, 10 + bob), (4 - stretch, 14), 2)
        pygame.draw.line(s, pal.UI_BG_MID, (8, 10 + bob), (9 + stretch, 14), 2)
        pygame.draw.line(s, pal.UI_BG_MID, (14, 10 + bob), (15 + stretch, 14), 2)
        pygame.draw.line(s, pal.UI_BG_MID, (16, 10 + bob), (13 - stretch, 14), 2)
        pygame.draw.ellipse(s, pal.UI_BG_MID, (4, 5 + bob, 13, 6))
        pygame.draw.ellipse(s, pal.UI_BG_LIGHT, (10, 4 + bob, 7, 6))
        pygame.draw.polygon(s, pal.UI_BG_LIGHT, [(15, 4 + bob), (20, 6 + bob), (15, 8 + bob)])
        pygame.draw.polygon(s, pal.UI_BG_MID, [(14, 2 + bob), (16, 2 + bob), (15, 5 + bob)])
        s.set_at((17, 5 + bob), pal.CRIMSON_LIGHT)
        s.set_at((19, 7 + bob), pal.STONE_HIGHLIGHT)
        pygame.draw.line(s, pal.UI_BG_MID, (4, 6 + bob), (1, 4 + bob + (f % 2)), 2)
        return s

    def _draw_knight(self, f: int) -> pygame.Surface:
        s = pygame.Surface((22, 22), pygame.SRCALPHA)
        bob = -1 if f in (1, 3) else 0
        l_off = -1 if f == 1 else (1 if f == 3 else 0)
        pygame.draw.polygon(s, pal.CRIMSON_DARK, [(4, 7 + bob), (8, 7 + bob), (6, 18), (2, 17)])
        pygame.draw.rect(s, pal.IRON_DARK, (8 + l_off, 16, 3, 4))
        pygame.draw.rect(s, pal.IRON_DARK, (12 - l_off, 16, 3, 4))
        pygame.draw.rect(s, pal.IRON_MID, (7, 8 + bob, 8, 8))
        pygame.draw.rect(s, pal.IRON_LIGHT, (8, 8 + bob, 6, 5))
        pygame.draw.rect(s, pal.IRON_LIGHT, (8, 3 + bob, 6, 5))
        pygame.draw.line(s, pal.OUTLINE_DARK, (10, 5 + bob), (13, 5 + bob), 1)
        pygame.draw.polygon(s, pal.CRIMSON_LIGHT, [(6, 2 + bob), (11, 1 + bob), (9, 4 + bob)])
        pygame.draw.rect(s, pal.IRON_DARK, (13, 8 + bob, 6, 9))
        pygame.draw.rect(s, pal.ROYAL_BLUE_DARK, (14, 9 + bob, 4, 7))
        pygame.draw.rect(s, pal.GOLD_LIGHT, (15, 10 + bob, 2, 5))
        return s

    def _draw_boss_golem(self, f: int) -> pygame.Surface:
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        bob = -1 if f in (1, 3) else 0
        l_off = -2 if f == 1 else (2 if f == 3 else 0)
        pygame.draw.rect(s, pal.STONE_DARK, (8 + l_off, 22, 6, 8))
        pygame.draw.rect(s, pal.STONE_DARK, (18 - l_off, 22, 6, 8))
        pygame.draw.polygon(s, pal.STONE_MID, [(5, 8 + bob), (27, 8 + bob), (24, 23 + bob), (8, 23 + bob)])
        pygame.draw.polygon(s, pal.STONE_LIGHT, [(7, 9 + bob), (22, 9 + bob), (20, 19 + bob), (9, 19 + bob)])
        pygame.draw.rect(s, pal.GRASS_MID, (5, 7 + bob, 7, 3))
        pygame.draw.rect(s, pal.GRASS_MID, (20, 7 + bob, 7, 3))
        pygame.draw.circle(s, pal.FIRE_DARK, (16, 15 + bob), 4)
        pygame.draw.circle(s, pal.FIRE_LIGHT, (16, 15 + bob), 3)
        pygame.draw.circle(s, pal.FIRE_CORE, (16, 15 + bob), 1)
        pygame.draw.rect(s, pal.STONE_LIGHT, (11, 3 + bob, 10, 6))
        pygame.draw.rect(s, pal.GOLD_MID, (12, 1 + bob, 8, 2))
        pygame.draw.rect(s, pal.FIRE_CORE, (13, 5 + bob, 2, 2))
        pygame.draw.rect(s, pal.FIRE_CORE, (18, 5 + bob, 2, 2))
        arm_y = 12 + bob + (2 if f in (1, 2) else 0)
        pygame.draw.rect(s, pal.STONE_DARK, (2, arm_y, 5, 9))
        pygame.draw.rect(s, pal.STONE_MID, (25, arm_y - 1, 5, 9))
        return s

    # ------------------------------------------------------------------
    # PROJECTILES & UI ICONS
    # ------------------------------------------------------------------
    def get_projectile_sprite(self, kind: str, angle_deg: float = 0.0) -> pygame.Surface:
        q_angle = int(round(angle_deg / 15.0) * 15) % 360 if kind in ("arrow", "frost") else 0
        key = ("proj", kind, q_angle, self.pixel_scale)
        if key in self._cache:
            return self._cache[key]

        s = pygame.Surface((12, 12), pygame.SRCALPHA)
        if kind == "arrow":
            pygame.draw.line(s, pal.WOOD_HIGHLIGHT, (2, 6), (9, 6), 2)
            pygame.draw.polygon(s, pal.IRON_SPECULAR, [(8, 4), (11, 6), (8, 8)])
            pygame.draw.line(s, pal.ARCHER_GREEN_LIGHT, (1, 5), (3, 5), 1)
            pygame.draw.line(s, pal.ARCHER_GREEN_LIGHT, (1, 7), (3, 7), 1)
            rot = pygame.transform.rotate(s, -q_angle)
            rw, rh = rot.get_size()
            c = pygame.Surface((12, 12), pygame.SRCALPHA)
            c.blit(rot, ((12 - rw) // 2, (12 - rh) // 2))
            s = c
        elif kind == "bomb":
            pygame.draw.circle(s, pal.IRON_DARK, (6, 6), 4)
            pygame.draw.circle(s, pal.IRON_MID, (5, 5), 2)
            s.set_at((4, 4), pal.IRON_SPECULAR)
            s.set_at((9, 3), pal.FIRE_CORE)
            s.set_at((8, 4), pal.FIRE_MID)
        elif kind == "frost":
            pygame.draw.polygon(s, pal.FROST_MID, [(2, 6), (6, 3), (10, 6), (6, 9)])
            pygame.draw.polygon(s, pal.FROST_CORE, [(4, 6), (6, 4), (8, 6), (6, 8)])
            rot = pygame.transform.rotate(s, -q_angle)
            rw, rh = rot.get_size()
            c = pygame.Surface((12, 12), pygame.SRCALPHA)
            c.blit(rot, ((12 - rw) // 2, (12 - rh) // 2))
            s = c
        elif kind == "meteor":
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(s, pal.FIRE_DARK, (8, 8), 6)
            pygame.draw.circle(s, pal.FIRE_MID, (8, 8), 5)
            pygame.draw.circle(s, pal.FIRE_LIGHT, (7, 7), 3)
            pygame.draw.circle(s, pal.FIRE_CORE, (6, 6), 2)

        outlined = apply_pixel_outline(s)
        res = upscale_pixel(outlined, max(2, self.pixel_scale - 1))
        self._cache[key] = res
        return res

    def get_icon(self, icon_name: str, scale_override: int | None = None) -> pygame.Surface:
        sc = scale_override if scale_override is not None else max(2, self.pixel_scale - 1)
        key = ("icon", icon_name, sc)
        if key in self._cache:
            return self._cache[key]

        s = pygame.Surface((12, 12), pygame.SRCALPHA)
        if icon_name == "coin":
            pygame.draw.circle(s, pal.GOLD_DARK, (6, 6), 5)
            pygame.draw.circle(s, pal.GOLD_LIGHT, (6, 6), 4)
            pygame.draw.line(s, pal.GOLD_SHINE, (5, 4), (5, 8), 1)
            pygame.draw.line(s, pal.GOLD_DARK, (6, 4), (6, 8), 1)
        elif icon_name == "heart":
            pygame.draw.circle(s, pal.CRIMSON_LIGHT, (4, 4), 3)
            pygame.draw.circle(s, pal.CRIMSON_LIGHT, (8, 4), 3)
            pygame.draw.polygon(s, pal.CRIMSON_LIGHT, [(1, 5), (11, 5), (6, 10)])
            s.set_at((3, 3), (255, 200, 200))
        elif icon_name == "wave":
            pygame.draw.rect(s, pal.STONE_HIGHLIGHT, (3, 2, 6, 6))
            pygame.draw.rect(s, pal.STONE_LIGHT, (4, 8, 4, 2))
            s.set_at((4, 5), pal.OUTLINE_DARK)
            s.set_at((7, 5), pal.OUTLINE_DARK)
        elif icon_name == "upgrade":
            pygame.draw.polygon(s, pal.GOLD_LIGHT, [(6, 1), (11, 6), (8, 6), (8, 10), (4, 10), (4, 6), (1, 6)])
            pygame.draw.polygon(s, pal.GOLD_SHINE, [(6, 2), (9, 5), (7, 5), (7, 9), (5, 9), (5, 5), (3, 5)])
        elif icon_name == "sell":
            pygame.draw.circle(s, pal.GOLD_MID, (6, 6), 4)
            pygame.draw.line(s, pal.CRIMSON_LIGHT, (3, 3), (9, 9), 2)
        elif icon_name == "target":
            pygame.draw.circle(s, pal.UI_CYAN, (6, 6), 4, 1)
            pygame.draw.line(s, pal.UI_CYAN, (6, 1), (6, 11), 1)
            pygame.draw.line(s, pal.UI_CYAN, (1, 6), (11, 6), 1)
        elif icon_name == "meteor":
            pygame.draw.circle(s, pal.FIRE_MID, (5, 7), 4)
            pygame.draw.circle(s, pal.FIRE_CORE, (4, 6), 2)
            pygame.draw.polygon(s, pal.FIRE_LIGHT, [(6, 4), (11, 1), (8, 7)])
        elif icon_name == "blizzard":
            pygame.draw.line(s, pal.FROST_LIGHT, (6, 1), (6, 11), 2)
            pygame.draw.line(s, pal.FROST_LIGHT, (1, 6), (11, 6), 2)
            pygame.draw.line(s, pal.FROST_CORE, (3, 3), (9, 9), 1)
            pygame.draw.line(s, pal.FROST_CORE, (9, 3), (3, 9), 1)
        elif icon_name in ("hero", "holy_strike"):
            # Golden Paladin Sword & Sunburst Icon
            pygame.draw.circle(s, pal.GOLD_MID, (6, 6), 4)
            pygame.draw.line(s, pal.IRON_SPECULAR, (6, 1), (6, 10), 2)
            pygame.draw.line(s, pal.GOLD_SHINE, (3, 4), (9, 4), 2)
            s.set_at((6, 1), pal.UI_TEXT_WHITE)

        outlined = apply_pixel_outline(s)
        res = upscale_pixel(outlined, sc)
        self._cache[key] = res
        return res

    # ------------------------------------------------------------------
    # ROYAL CASTLE (RIGHT END OF PATH) & DARK PORTAL (LEFT ENTRANCE)
    # ------------------------------------------------------------------
    def get_castle_sprite(self, hp_ratio: float = 1.0) -> pygame.Surface:
        stage = 0 if hp_ratio > 0.66 else (1 if hp_ratio > 0.33 else 2)
        key = ("castle", stage, self.pixel_scale)
        if key in self._cache:
            return self._cache[key]

        s = pygame.Surface((48, 52), pygame.SRCALPHA)
        pygame.draw.rect(s, pal.STONE_DARK, (8, 18, 32, 30))
        pygame.draw.rect(s, pal.STONE_MID, (10, 19, 28, 28))
        for tx in (3, 33):
            pygame.draw.rect(s, pal.STONE_DARK, (tx, 10, 12, 38))
            pygame.draw.rect(s, pal.STONE_LIGHT, (tx + 1, 11, 8, 36))
            if stage < 2 or tx == 3:
                pygame.draw.polygon(s, pal.ROYAL_BLUE_DARK, [(tx - 1, 10), (tx + 13, 10), (tx + 6, 1)])
                pygame.draw.polygon(s, pal.ROYAL_BLUE_LIGHT, [(tx, 10), (tx + 6, 10), (tx + 6, 2)])
                s.set_at((tx + 6, 0), pal.GOLD_SHINE)
        for bx in range(10, 36, 4):
            pygame.draw.rect(s, pal.STONE_LIGHT, (bx, 15, 3, 3))
        pygame.draw.rect(s, pal.ROYAL_BLUE_LIGHT, (7, 22, 4, 9))
        pygame.draw.rect(s, pal.GOLD_LIGHT, (8, 24, 2, 5))
        pygame.draw.rect(s, pal.ROYAL_BLUE_LIGHT, (37, 22, 4, 9))
        pygame.draw.rect(s, pal.GOLD_LIGHT, (38, 24, 2, 5))
        pygame.draw.rect(s, pal.OUTLINE_DARK, (17, 28, 14, 20))
        pygame.draw.circle(s, pal.OUTLINE_DARK, (24, 28), 7)
        pygame.draw.rect(s, pal.WOOD_DARK, (18, 28, 12, 19))
        pygame.draw.circle(s, pal.WOOD_MID, (24, 28), 6)
        for gx in range(19, 30, 3):
            pygame.draw.line(s, pal.IRON_LIGHT, (gx, 24), (gx, 47), 1)
        pygame.draw.line(s, pal.GOLD_MID, (17, 28), (31, 28), 1)

        if stage >= 1:
            pygame.draw.line(s, pal.OUTLINE_DARK, (14, 20), (18, 26), 1)
            pygame.draw.line(s, pal.OUTLINE_DARK, (30, 19), (27, 25), 1)
        if stage >= 2:
            pygame.draw.circle(s, pal.FIRE_MID, (38, 12), 3)
            pygame.draw.circle(s, pal.FIRE_LIGHT, (38, 11), 2)
            pygame.draw.circle(s, pal.FIRE_MID, (13, 22), 2)

        outlined = apply_pixel_outline(s)
        res = upscale_pixel(outlined, self.pixel_scale)
        self._cache[key] = res
        return res
