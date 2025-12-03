import pygame
from typing import Any, Dict, List

def get_buttons(engine: Any) -> List[Dict[str, Any]]:
    w = 220
    h = 44
    x = engine.width - w - 10
    y0 = 80
    gap = 10
    return [
        {'type': 'sword', 'cost': engine.UPGRADE_COSTS['sword'], 'label': 'sword', 'rect': pygame.Rect(x, y0 + 0*(h+gap), w, h)},
        {'type': 'range', 'cost': engine.UPGRADE_COSTS['range'], 'label': 'range', 'rect': pygame.Rect(x, y0 + 1*(h+gap), w, h)},
        {'type': 'bullet_power', 'cost': engine.UPGRADE_COSTS['bullet_power'], 'label': 'bullet_power', 'rect': pygame.Rect(x, y0 + 2*(h+gap), w, h)},
        {'type': 'bullet_speed', 'cost': engine.UPGRADE_COSTS['bullet_speed'], 'label': 'bullet_speed', 'rect': pygame.Rect(x, y0 + 3*(h+gap), w, h)},
    ]

def apply_upgrade(engine: Any, up_type: str) -> None:
    if not engine.towers:
        return
    
    # Check level limit
    lvl = engine.upgrade_levels.get(up_type, 0)
    limit = engine.upgrade_limits.get(up_type, 99)
    if lvl >= limit:
        return

    idx = engine.selected_tower_idx if (engine.selected_tower_idx is not None and 0 <= engine.selected_tower_idx < len(engine.towers)) else 0
    t = engine.towers[idx]
    
    if up_type == 'range':
        t['range'] = int(t['range'] * 2.0)
    elif up_type == 'firerate':
        delta = engine.FIRERATE_DELTA if hasattr(engine, 'FIRERATE_DELTA') else 50
        t['fire_rate'] = max(100, t['fire_rate'] - delta)
    elif up_type == 'bullet':
        engine.bullet_speed += engine.BULLET_SPEED_DELTA if hasattr(engine, 'BULLET_SPEED_DELTA') else 30
        engine.bullet_damage += engine.BULLET_DAMAGE_DELTA if hasattr(engine, 'BULLET_DAMAGE_DELTA') else 1
    elif up_type == 'bullet_power':
        engine.bullet_damage += engine.BULLET_DAMAGE_DELTA if hasattr(engine, 'BULLET_DAMAGE_DELTA') else 1
    elif up_type == 'bullet_speed':
        engine.bullet_speed += engine.BULLET_SPEED_DELTA if hasattr(engine, 'BULLET_SPEED_DELTA') else 30
    elif up_type == 'sword':
        if engine.sword_level == 0:
            engine.sword_damage = engine.SWORD_DAMAGE_BASE
        else:
            engine.sword_damage += engine.SWORD_DAMAGE_DELTA
        engine.sword_level += 1
        # Sword upgrade increases level directly in engine logic, so we manually inc here for consistency with others if needed
        # But actually we should increment the tracking dict for all types
        
    # Increment level tracker
    if up_type in engine.upgrade_levels:
        engine.upgrade_levels[up_type] += 1
        
    from engine.render import spawn_upgrade_particles as _sup
    _sup(engine, t['pos'])
