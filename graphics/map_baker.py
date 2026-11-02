from __future__ import annotations
import math
import random
import pygame
from graphics import palette as pal
from graphics.pixel_gen import apply_pixel_outline
from gameplay.path import RoadPath


def bake_pixel_map(
    width: int,
    height: int,
    road: RoadPath,
    pixel_scale: int = 4,
    seed: int = 42,
    biome: str = "grasslands",
) -> pygame.Surface:
    """Bakes a rich procedural pixel-art fantasy battleground for the selected biome."""
    rng = random.Random(seed + (101 if biome == "frost_tundra" else (202 if biome == "volcanic_ash" else 0)))
    vw = max(160, width // pixel_scale)
    vh = max(90, height // pixel_scale)
    canvas = pygame.Surface((vw, vh))

    if biome == "frost_tundra":
        g_deep, g_base, g_mid, g_light, g_hi = (
            pal.TUNDRA_DEEP,
            pal.TUNDRA_BASE,
            pal.TUNDRA_MID,
            pal.TUNDRA_LIGHT,
            pal.TUNDRA_HIGHLIGHT,
        )
        p_dark, p_mid, p_light = pal.TUNDRA_PATH_DARK, pal.TUNDRA_PATH_MID, pal.TUNDRA_PATH_LIGHT
        r_deep, r_mid, r_foam = pal.FROST_DARK, pal.FROST_MID, pal.FROST_CORE
        shadow_col = (115, 145, 175)
    elif biome == "volcanic_ash":
        g_deep, g_base, g_mid, g_light, g_hi = (
            pal.ASH_DEEP,
            pal.ASH_BASE,
            pal.ASH_MID,
            pal.ASH_LIGHT,
            pal.ASH_HIGHLIGHT,
        )
        p_dark, p_mid, p_light = pal.ASH_PATH_DARK, pal.ASH_PATH_MID, pal.ASH_PATH_LIGHT
        r_deep, r_mid, r_foam = pal.LAVA_DEEP, pal.LAVA_MID, pal.LAVA_BRIGHT
        shadow_col = (28, 22, 30)
    else:
        g_deep, g_base, g_mid, g_light, g_hi = (
            pal.GRASS_DEEP,
            pal.GRASS_BASE,
            pal.GRASS_MID,
            pal.GRASS_LIGHT,
            pal.GRASS_HIGHLIGHT,
        )
        p_dark, p_mid, p_light = pal.PATH_DIRT_DARK, pal.PATH_DIRT_MID, pal.PATH_DIRT_LIGHT
        r_deep, r_mid, r_foam = pal.WATER_DEEP, pal.WATER_MID, pal.WATER_FOAM
        shadow_col = (28, 58, 38)

    canvas.fill(g_base)

    # 1. Organic terrain patches (low-frequency value noise)
    for y in range(vh):
        for x in range(vw):
            n = (
                math.sin(x * 0.08 + y * 0.05)
                + math.cos(x * 0.04 - y * 0.09)
                + math.sin((x + y) * 0.03)
            )
            if n > 1.15:
                canvas.set_at((x, y), g_light if (x + y) % 2 == 0 else g_mid)
            elif n > 0.25:
                canvas.set_at((x, y), g_mid)
            elif n < -1.10:
                canvas.set_at((x, y), g_deep)

    # 2. Winding River / Glacial Stream / Molten Lava Channel cutting North-to-South
    river_points = []
    for y in range(vh):
        yp = y / float(vh)
        rx = int(vw * (0.475 + 0.025 * math.sin(yp * math.pi * 2.2)))
        river_points.append((rx, y))
        rw = 6
        pygame.draw.circle(canvas, p_dark, (rx, y), rw + 2)
    for rx, y in river_points:
        pygame.draw.circle(canvas, r_deep, (rx, y), 6)
        pygame.draw.circle(canvas, r_mid, (rx - 1, y), 4)
        if y % 4 == 0:
            canvas.set_at((max(0, min(vw - 1, rx - 2 + (y % 3))), y), r_foam)

    # 3. Sample road points in virtual coordinates
    v_waypoints = [(wx / float(width) * vw, wy / float(height) * vh) for wx, wy in road.waypoints]
    v_slots = [(sl.pos[0] / float(width) * vw, sl.pos[1] / float(height) * vh) for sl in road.slots]

    # Outer road border / shoulder
    for vx, vy in v_waypoints:
        pygame.draw.circle(canvas, pal.OUTLINE_DARK, (int(vx), int(vy)), 10)
    for vx, vy in v_waypoints:
        pygame.draw.circle(canvas, p_dark, (int(vx), int(vy)), 9)
    for vx, vy in v_waypoints:
        pygame.draw.circle(canvas, p_mid, (int(vx), int(vy)), 7)

    # Individual cobblestone bricks along the road
    for i in range(0, len(v_waypoints), 2):
        vx, vy = v_waypoints[i]
        for _ in range(4):
            ox = rng.randint(-6, 5)
            oy = rng.randint(-6, 5)
            if ox * ox + oy * oy <= 38:
                col = rng.choice([pal.STONE_MID, pal.STONE_LIGHT, p_light, pal.STONE_DARK])
                pygame.draw.rect(canvas, col, (int(vx + ox), int(vy + oy), 2, 2))

    # 4. Stone Bridge where road crosses river (~ x_pct=0.475, y_pct=0.745)
    bx = int(vw * 0.475)
    by = int(vh * 0.745)
    pygame.draw.rect(canvas, pal.OUTLINE_DARK, (bx - 11, by - 10, 22, 20))
    pygame.draw.rect(canvas, pal.STONE_DARK, (bx - 10, by - 9, 20, 18))
    deck_col = pal.IRON_MID if biome == "volcanic_ash" else pal.WOOD_MID
    plank_col = pal.IRON_LIGHT if biome == "volcanic_ash" else pal.WOOD_LIGHT
    pygame.draw.rect(canvas, deck_col, (bx - 9, by - 6, 18, 12))
    for plank_x in range(bx - 8, bx + 9, 3):
        pygame.draw.line(canvas, plank_col, (plank_x, by - 6), (plank_x, by + 5), 1)
    for rail_x in range(bx - 10, bx + 10, 4):
        pygame.draw.rect(canvas, pal.STONE_LIGHT, (rail_x, by - 9, 3, 2))
        pygame.draw.rect(canvas, pal.STONE_LIGHT, (rail_x, by + 7, 3, 2))

    # 5. Biome surface details away from road/river
    def _is_clear(tx: float, ty: float, min_road: float = 14.0, min_slot: float = 14.0) -> bool:
        ry_idx = max(0, min(vh - 1, int(ty)))
        rx_river = river_points[ry_idx][0]
        if abs(tx - rx_river) < 11:
            return False
        for wx, wy in v_waypoints[::2]:
            if math.hypot(tx - wx, ty - wy) < min_road:
                return False
        for sx, sy in v_slots:
            if math.hypot(tx - sx, ty - sy) < min_slot:
                return False
        if tx > vw * 0.84 and 0.30 * vh < ty < 0.70 * vh:
            return False
        if tx < vw * 0.08 and 0.18 * vh < ty < 0.42 * vh:
            return False
        return True

    for _ in range(280):
        gx = rng.randint(4, vw - 5)
        gy = rng.randint(4, vh - 5)
        if _is_clear(gx, gy, min_road=12.0, min_slot=11.0):
            canvas.set_at((gx, gy), g_hi)
            canvas.set_at((gx + 1, gy + 1), g_deep)
            if rng.random() < 0.16:
                if biome == "frost_tundra":
                    fcol = rng.choice([pal.FROST_LIGHT, pal.FROST_CORE, (200, 230, 255)])
                elif biome == "volcanic_ash":
                    fcol = rng.choice([pal.FIRE_MID, pal.FIRE_LIGHT, pal.LAVA_BRIGHT])
                else:
                    fcol = rng.choice([(250, 220, 70), (240, 95, 110), (140, 210, 255), (255, 255, 255)])
                canvas.set_at((gx, gy - 1), fcol)

    # 6. Rocks & Boulders
    rock_surf = pygame.Surface((10, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(rock_surf, pal.STONE_DARK, (1, 2, 8, 5))
    pygame.draw.ellipse(rock_surf, pal.STONE_MID, (2, 2, 6, 4))
    pygame.draw.ellipse(rock_surf, pal.FROST_LIGHT if biome == "frost_tundra" else pal.STONE_LIGHT, (2, 2, 4, 2))
    rock_outlined = apply_pixel_outline(rock_surf)

    for _ in range(28):
        rx = rng.randint(8, vw - 14)
        ry = rng.randint(14, vh - 12)
        if _is_clear(rx, ry, min_road=15.0, min_slot=14.0):
            canvas.blit(rock_outlined, (rx - 5, ry - 4))

    # 7. Biome-Specific Pixel-Art Trees (sorted top-to-bottom for depth overlap)
    tree_positions = []
    for _ in range(95):
        tx = rng.randint(6, vw - 10)
        ty = rng.randint(16, vh - 8)
        is_edge = tx < 24 or tx > vw - 24 or ty < 28 or ty > vh - 22
        if (is_edge or rng.random() < 0.35) and _is_clear(tx, ty, min_road=17.0, min_slot=16.0):
            if all(math.hypot(tx - ox, ty - oy) > 10 for ox, oy in tree_positions):
                tree_positions.append((tx, ty))

    tree_positions.sort(key=lambda p: p[1])
    for tx, ty in tree_positions:
        t_surf = pygame.Surface((16, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(canvas, shadow_col, (tx - 6, ty + 4, 12, 5))

        if biome == "frost_tundra":
            # Snow-covered Northern Pine
            pygame.draw.rect(t_surf, pal.TREE_TRUNK_DARK, (7, 14, 3, 4))
            pygame.draw.polygon(t_surf, pal.PINE_DARK, [(2, 14), (14, 14), (8, 6)])
            pygame.draw.polygon(t_surf, pal.PINE_MID, [(3, 10), (13, 10), (8, 3)])
            pygame.draw.polygon(t_surf, pal.PINE_SNOW, [(4, 7), (12, 7), (8, 2)])
            pygame.draw.line(t_surf, pal.PINE_SNOW, (3, 13), (12, 13), 1)
        elif biome == "volcanic_ash":
            # Charred Volcanic Tree with glowing ember crown
            pygame.draw.rect(t_surf, (45, 32, 34), (6, 11, 4, 7))
            pygame.draw.line(t_surf, (58, 40, 42), (7, 11), (3, 6), 2)
            pygame.draw.line(t_surf, (58, 40, 42), (8, 10), (12, 5), 2)
            pygame.draw.line(t_surf, (58, 40, 42), (8, 9), (8, 4), 2)
            if rng.random() < 0.65:
                pygame.draw.circle(t_surf, pal.FIRE_DARK, (4, 6), 2)
                pygame.draw.circle(t_surf, pal.FIRE_MID, (12, 5), 2)
                t_surf.set_at((8, 4), pal.FIRE_CORE)
        else:
            # Classic Royal Oak / Autumn Tree
            pygame.draw.rect(t_surf, pal.TREE_TRUNK_DARK, (6, 12, 4, 6))
            pygame.draw.rect(t_surf, pal.TREE_TRUNK_LIGHT, (7, 12, 2, 5))
            is_autumn = rng.random() < 0.12
            c_dark = (142, 68, 32) if is_autumn else pal.LEAF_DARK
            c_mid = pal.LEAF_AUTUMN if is_autumn else pal.LEAF_MID
            c_light = pal.GOLD_LIGHT if is_autumn else pal.LEAF_LIGHT
            pygame.draw.circle(t_surf, c_dark, (8, 10), 6)
            pygame.draw.circle(t_surf, c_mid, (8, 8), 5)
            pygame.draw.circle(t_surf, c_light, (7, 6), 3)

        t_out = apply_pixel_outline(t_surf)
        canvas.blit(t_out, (tx - 9, ty - 13))

    # 8. Dark Enemy Spawn Portal / Skull Arch on Left Entrance
    ex, ey = int(vw * 0.025), int(vh * 0.30)
    portal = pygame.Surface((20, 24), pygame.SRCALPHA)
    pygame.draw.ellipse(portal, pal.STONE_DARK, (1, 2, 18, 20))
    pygame.draw.ellipse(portal, pal.ARCANE_DARK, (4, 5, 12, 15))
    pygame.draw.ellipse(portal, pal.ARCANE_MID, (6, 7, 8, 11))
    pygame.draw.ellipse(portal, pal.ARCANE_LIGHT, (8, 9, 4, 7))
    p_out = apply_pixel_outline(portal)
    canvas.blit(p_out, (ex - 10, ey - 13))

    return pygame.transform.scale(canvas, (width, height))
