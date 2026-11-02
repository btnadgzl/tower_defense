# Tower Defense II — Royal Guard (Tactical Pixel-Art Edition)

## Overview
**Tower Defense II: Royal Guard** is a modular 2D fantasy tower defense game built in **Python** and **Pygame**. Inspired by tactical slot-based defense games like *Kingdom Rush*, it features a custom **Procedural Pixel-Art & Terrain Baking Engine** (`graphics/pixel_gen.py`, `graphics/map_baker.py`) that renders multi-part evolving towers, animated enemy units, curved cobblestone paths, and dynamic UI panels entirely in code without relying on static sprite sheets.

> **Note:** The original v1 prototype is preserved in the [`legacy_v1/`](./legacy_v1) directory for historical reference.

---

## Key Features & Architecture
- **Procedural Pixel-Art Engine (`graphics/`):**
  - Generates multi-layered sprites on low-resolution virtual canvases with automatic 1px dark contour generation (`apply_pixel_outline`), directional shading, and crisp nearest-neighbor scaling.
  - Bakes a complete fantasy battleground (`bake_pixel_map`) featuring a Catmull-Rom spline cobblestone road, azure river, stone bridge, forest groves, and the Royal Castle.
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
├── core/               # Event bus, logging, and balance/settings configuration
├── graphics/           # Procedural pixel-art sprite generator, map baker, and UI kit
├── gameplay/           # Spline pathing, towers, enemies, pooled projectiles, and waves
├── systems/            # Pixel particle/shockwave system and audio controller
├── ui/                 # Tactical radial menu, HUD, and menu/overlay screens
├── assets/             # Audio tracks (.wav) and pixel font
├── legacy_v1/          # Archived v1.0 prototype
├── game.py             # Main game engine and primary loop
└── settings.json       # Persistent user configuration and high score records
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
| **Right Click / `ESC`** | Close active Radial Menu / Toggle Pause Menu |
| **`1` / `2` / `3` / `4`** | Build Archer / Artillery / Frost / Arcane tower on selected empty slot |
| **`U`** | Upgrade selected tower to next tier (Lv.2 / Lv.3) |
| **`T`** | Cycle selected tower's targeting strategy (`First` / `Strongest` / `Weakest` / `Nearest`) |
| **`S` / `Backspace`** | Sell selected tower (75% gold refund) |
| **`N`** | Call next wave early (grants Early Wave Gold Bonus) |
| **`Space`** | Toggle game speed (`1x` / `2x`) |
| **`Q` / `W`** | Cast **Meteor Shower** (`Q`) / **Royal Blizzard** (`W`) |
