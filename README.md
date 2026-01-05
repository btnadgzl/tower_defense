# Game Trial

## Overview
- A simple **Tower Defense** game built with a **modular architecture**.
- Implements **Event/Observer**, **Strategy**, and **Factory** design patterns.
- Can be executed as a standalone `.exe` or from the Python source code.

## Features
- **Event-driven** input and UI management (`core/events.py`).
- **Targeting strategies** for sophisticated enemy selection (`gameplay/strategy.py`).
- **Entity Factory** for dynamic object creation (`engine/factory.py`).
- Efficient bullet management using a simple **Object Pool** (`engine/pool.py`).
- Modernized and responsive UI elements (`ui/elements.py`).

## How to Run

### Via Standalone Executable
- **PowerShell:**
  ```powershell
  & ".\OyunDeneme.exe"

  Manual Launch: Navigate to the folder and double-click OyunDeneme.exe.

From Source Code
Python 3.12+ is recommended.
Packaging (PyInstaller)
To generate a standalone .exe file:

Build Command:
pyinstaller --noconfirm --clean --onefile --name OyunDeneme "game.py" --add-data "assets;assets" --add-data "settings.json;."
Note: Add the --windowed flag to hide the console window upon launch.
Project Structure
assets/: Game visuals and audio files.
core/: Core events, logging, and configuration loader.
engine/: Rendering, transitions, upgrades, factory, and object pooling.
gameplay/: Towers, enemies, bullets, and targeting strategies.
systems/: Input, sound, and scoring systems.
ui/: HUD, menus, overlays, settings, upgrades, and UIElement base class.
game.py: Main game engine and the primary game loop.
settings.json: User-defined configurations.

Settings (settings.json)
Key,Value Range / Type
music_volume,0.0–1.0
sfx_volume,0.0–1.0
fullscreen,true / false
show_fps,true / false
difficulty,easy

Controls
Space: Manual Fire
U: Toggle Upgrade Panel
Q: Use Ultimate Ability
Esc: Pause / Resume
1 / 2 / 3: Upgrade Shortcuts (Range / Fire Rate / Bullet)
Debug Keys: F1-F10, Tab, Ctrl+S

Troubleshooting
Asset Loading in EXE: The code supports bundled paths using sys._MEIPASS for PyInstaller compatibility.
Event Errors: Ensure Event and constants are imported at the top of UI modules.

License and Assets
Asset files should be licensed according to their original terms. Please include appropriate licensing documentation when sharing externally.
