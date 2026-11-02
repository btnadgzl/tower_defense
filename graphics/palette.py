from __future__ import annotations
from typing import Tuple

Color = Tuple[int, int, int]
ColorA = Tuple[int, int, int, int]

# --- Core Outline & Shadow ---
OUTLINE_DARK: Color = (22, 18, 30)
OUTLINE_SOFT: Color = (38, 33, 50)
SHADOW_ALPHA: ColorA = (12, 10, 20, 110)

# --- Nature / Grass Ramps ---
GRASS_DEEP: Color = (42, 92, 55)
GRASS_BASE: Color = (56, 118, 64)
GRASS_MID: Color = (72, 140, 72)
GRASS_LIGHT: Color = (98, 166, 84)
GRASS_HIGHLIGHT: Color = (128, 190, 96)

TREE_TRUNK_DARK: Color = (74, 46, 33)
TREE_TRUNK_LIGHT: Color = (106, 68, 46)
LEAF_DARK: Color = (30, 72, 46)
LEAF_MID: Color = (46, 104, 56)
LEAF_LIGHT: Color = (76, 142, 68)
LEAF_AUTUMN: Color = (196, 112, 52)

WATER_DEEP: Color = (36, 82, 136)
WATER_MID: Color = (52, 116, 176)
WATER_FOAM: Color = (165, 222, 245)

# --- Cobblestone Path & Castle Stone Ramps ---
PATH_DIRT_DARK: Color = (108, 84, 62)
PATH_DIRT_MID: Color = (132, 104, 76)
PATH_DIRT_LIGHT: Color = (156, 126, 94)

STONE_DARK: Color = (78, 80, 94)
STONE_MID: Color = (112, 116, 132)
STONE_LIGHT: Color = (150, 155, 170)
STONE_HIGHLIGHT: Color = (188, 192, 205)

# --- Wood & Leather Ramps ---
WOOD_DARK: Color = (82, 48, 30)
WOOD_MID: Color = (122, 74, 44)
WOOD_LIGHT: Color = (162, 104, 62)
WOOD_HIGHLIGHT: Color = (196, 136, 84)

# --- Metal & Armor Ramps ---
IRON_DARK: Color = (52, 56, 68)
IRON_MID: Color = (84, 92, 108)
IRON_LIGHT: Color = (130, 140, 160)
IRON_SPECULAR: Color = (205, 215, 230)

GOLD_DARK: Color = (168, 104, 24)
GOLD_MID: Color = (222, 158, 38)
GOLD_LIGHT: Color = (250, 208, 72)
GOLD_SHINE: Color = (255, 245, 170)

# --- Elemental / Tower Magic Ramps ---
ARCHER_GREEN_DARK: Color = (40, 110, 56)
ARCHER_GREEN_MID: Color = (68, 162, 78)
ARCHER_GREEN_LIGHT: Color = (125, 218, 110)

FIRE_DARK: Color = (165, 42, 32)
FIRE_MID: Color = (228, 92, 38)
FIRE_LIGHT: Color = (252, 168, 52)
FIRE_CORE: Color = (255, 240, 150)

FROST_DARK: Color = (38, 108, 168)
FROST_MID: Color = (72, 168, 232)
FROST_LIGHT: Color = (145, 225, 255)
FROST_CORE: Color = (230, 250, 255)

ARCANE_DARK: Color = (92, 38, 148)
ARCANE_MID: Color = (152, 72, 224)
ARCANE_LIGHT: Color = (208, 135, 255)
ARCANE_CORE: Color = (248, 220, 255)

# --- Enemy Colors ---
GOBLIN_SKIN_DARK: Color = (64, 118, 44)
GOBLIN_SKIN_LIGHT: Color = (104, 168, 62)
ORC_SKIN_DARK: Color = (48, 92, 48)
ORC_SKIN_LIGHT: Color = (78, 136, 68)
CRIMSON_DARK: Color = (132, 28, 38)
CRIMSON_LIGHT: Color = (198, 52, 58)
ROYAL_BLUE_DARK: Color = (36, 68, 142)
ROYAL_BLUE_LIGHT: Color = (68, 118, 212)

# --- UI Panel Colors ---
UI_BG_DARK: Color = (28, 24, 38)
UI_BG_MID: Color = (44, 38, 58)
UI_BG_LIGHT: Color = (64, 56, 82)
UI_BORDER_OUTER: Color = (18, 14, 24)
UI_BORDER_GOLD: Color = (212, 158, 52)
UI_TEXT_WHITE: Color = (245, 242, 232)
UI_TEXT_MUTED: Color = (172, 166, 186)
UI_RED: Color = (220, 62, 68)
UI_GREEN: Color = (78, 198, 96)
UI_CYAN: Color = (88, 200, 245)

