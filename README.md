# Tower Defense II — Royal Guard (Tactical Pixel-Art Edition)

## Overview
**Tower Defense II: Royal Guard** is a modular 2D fantasy tower defense game built in **Python** and **Pygame**. Inspired by tactical slot-based defense games like *Kingdom Rush*, it features a custom **Procedural Pixel-Art & Terrain Baking Engine** (`graphics/pixel_gen.py`, `graphics/map_baker.py`) paired with a **Real-Time 2D Dynamic Lighting & Additive Bloom Pipeline** (`graphics/lighting.py`), a **Living World & Persistent Battlefield Decal System** (`systems/world_fx.py`), a **Controllable Royal Paladin Hero Unit** (`gameplay/hero.py`), and **3 Distinct Procedural Fantasy Biomes**—all rendered in code without relying on external static sprite sheets.

> **Note:** The original v1 prototype is preserved in the [`legacy_v1/`](./legacy_v1) directory for historical reference.

---

## Key Features & Architecture
- **Procedural Pixel-Art Engine (`graphics/`):**
  - Generates multi-layered sprites on low-resolution virtual canvases with automatic 1px dark contour generation (`apply_pixel_outline`), directional shading, and crisp nearest-neighbor scaling.
  - Bakes complete procedural fantasy battlegrounds (`bake_pixel_map`) across 3 distinct biomes with Catmull-Rom spline cobblestone paths, winding water/lava channels, bridges, foliage, and the Royal Castle.
- **3 Procedural Biomes (`core/config.py`, `graphics/map_baker.py`):**
  1. **Emerald Grasslands:** Lush royal meadows with an azure river, oak groves, and floating forest leaves.
  2. **Frozen Tundra:** Snow-dusted northern pass with a glacial blue stream, snow-capped pines, and blizzard flurries.
  3. **Volcanic Ashlands:** Scorched obsidian crags split by a glowing molten lava river, burning ember trees, and rising ash particles.
- **Controllable Hero Unit — Sir Roland the Royal Paladin (`gameplay/hero.py`):**
  - Real-time command via **Right Click** or **`[H]`** to reposition anywhere across the battlefield.
  - Intercepts and blocks marching enemies in close melee combat with cleaving sword strikes that damage surrounding foes.
  - Persistent leveling system (Levels 1 to 5) that boosts Max HP and attack damage through combat XP.
  - **`[E]` Holy Judgment Skill:** Slams the ground with a consecrated golden sigil, healing the hero, dealing heavy AoE magic damage, and slowing all caught enemies.
  - Automatic respawn timer if knocked out in battle.
- **Real-Time 2D Dynamic Lighting & Bloom (`graphics/lighting.py`):**
  - Smooth Day -> Sunset -> Night progression across campaign waves (or manual mode cycling via **`[L]`**).
  - Multiplicative ambient lightmap (`BLEND_RGB_MULT`) combined with an additive HDR-style bloom pass (`BLEND_RGB_ADD`) for glowing Frost/Arcane spires, hero holy aura, castle torches, enemy spawn portal, Boss Golem magma core, molten lava river, projectiles, and falling meteors.
- **Living World & Persistent Battlefield Decals (`systems/world_fx.py`):**
  - Persistent fading ground decals: artillery/meteor scorch craters, frost spire ice patches, holy judgment sigils, and combat splats.
  - Animated river/lava current foam ripples, wind-blown biome foliage/embers, and glowing night fireflies.
- **Software Design Patterns:**
  - **Observer / Event Bus (`core/events.py`):** Decouples gameplay events, audio playback, and UI state transitions via `EventManager`.
  - **Strategy Pattern (`gameplay/strategy.py`):** Per-tower selectable targeting priorities (`First`, `Strongest`, `Weakest`, `Nearest`).
  - **Object Pool (`gameplay/projectiles.py`):** Reuses `Projectile` instances via `ProjectilePool` to eliminate frame-time garbage collection spikes.
- **4 Evolving Tower Archetypes (3 Upgrade Tiers Each):**
  1. **Archer Tower (`[1]`):** High fire rate single-target physical attacks with scaling critical strike chance (`10% -> 28%`).
  2. **Royal Artillery (`[2]`):** Fires parabolic mortar shells that deal heavy Area of Effect (AoE) explosive splash damage.
  3. **Frost Spire (`[3]`):** Unleashes an icy nova that deals magic damage and slows enemies within its blast radius.
  4. **Arcane Obelisk (`[4]`):** Strikes with armor-piercing Chain Lightning that arcs across multiple nearby enemies.
- **5 Distinct Enemy Classes (`gameplay/enemies.py`):**
  - *Goblin Scout* (fast, unarmored), *Orc Warrior* (balanced bruiser), *Shadow Warg* (high-speed pack unit), *Dark Knight* (50% physical armor), and *Ancient Stone Golem* (multi-phase Boss unit).
- **Active Kingdom Spells:**
  - **`[Q]` Meteor Shower:** Calls down 6 fiery meteors onto leading enemies, dealing heavy AoE explosive damage and applying burn DoT.
  - **`[W]` Royal Blizzard:** Freezes and slows all enemies across the battlefield while repairing the Royal Castle (`+15 HP`).

---

## Project Structure
```text
├── core/               # Event bus, logging, biome definitions, and balance/settings configuration
├── graphics/           # Procedural pixel-art generator, multi-biome map baker, 2D lighting/bloom, UI kit
├── gameplay/           # Hero unit, spline pathing, towers, enemies, pooled projectiles, and waves
├── systems/            # Pixel particles, persistent ground decals, biome ambient FX, and audio
├── ui/                 # Tactical radial menu, HUD with hero status card, and menu/overlay screens
├── assets/             # Audio tracks (.wav) and pixel font
├── legacy_v1/          # Archived v1.0 prototype
├── game.py             # Main game engine and primary loop
└── settings.json       # Persistent user configuration, high scores, and selected biome
```

---

## How to Run

### Prerequisites
- Python 3.10+
- `pygame` (`pip install pygame`)

### Launch Game
```bash
python game.py
# or on Windows PowerShell:
py game.py
```

---

## Controls

| Input / Key | Action |
| :--- | :--- |
| **Left Click** | Select tactical build slots, interact with Radial Menu & HUD buttons |
| **Right Click** | Close active Radial Menu / Command Hero to rally and intercept at mouse position |
| **`ESC`** | Close Radial Menu / Toggle Pause Menu |
| **`H`** | Rally Hero to current mouse cursor position |
| **`E`** | Cast Hero Active Skill (**Holy Judgment**) |
| **`1` / `2` / `3` / `4`** | Build Archer / Artillery / Frost / Arcane tower on selected empty slot |
| **`U`** | Upgrade selected tower to next tier (Lv.2 / Lv.3) |
| **`T`** | Cycle selected tower's targeting strategy (`First` / `Strongest` / `Weakest` / `Nearest`) |
| **`S` / `Backspace`** | Sell selected tower (75% gold refund) |
| **`L`** | Cycle Dynamic 2D Lighting mode (`Auto Cycle` / `Daylight` / `Sunset` / `Night`) |
| **`N`** | Call next wave early (grants Early Wave Gold Bonus) |
| **`Space`** | Toggle game speed (`1x` / `2x`) |
| **`Q` / `W`** | Cast **Meteor Shower** (`Q`) / **Royal Blizzard** (`W`) |
