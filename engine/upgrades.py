import pygame

def get_buttons(engine):
    w = 220
    h = 44
    x = engine.width - w - 10
    y0 = 80
    gap = 10
    return [
        {'type': 'range', 'cost': engine.UPGRADE_COSTS['range'], 'label': 'range', 'rect': pygame.Rect(x, y0 + 0*(h+gap), w, h)},
        {'type': 'firerate', 'cost': engine.UPGRADE_COSTS['firerate'], 'label': 'firerate', 'rect': pygame.Rect(x, y0 + 1*(h+gap), w, h)},
        {'type': 'bullet', 'cost': engine.UPGRADE_COSTS['bullet'], 'label': 'bullet', 'rect': pygame.Rect(x, y0 + 2*(h+gap), w, h)},
    ]

def apply_upgrade(engine, up_type):
    if not engine.towers:
        return
    idx = engine.selected_tower_idx if (engine.selected_tower_idx is not None and 0 <= engine.selected_tower_idx < len(engine.towers)) else 0
    t = engine.towers[idx]
    if up_type == 'range':
        t['range'] += engine.RANGE_UP_AMOUNT if hasattr(engine, 'RANGE_UP_AMOUNT') else 20
    elif up_type == 'firerate':
        delta = engine.FIRERATE_DELTA if hasattr(engine, 'FIRERATE_DELTA') else 50
        t['fire_rate'] = max(100, t['fire_rate'] - delta)
    elif up_type == 'bullet':
        engine.bullet_speed += engine.BULLET_SPEED_DELTA if hasattr(engine, 'BULLET_SPEED_DELTA') else 30
        engine.bullet_damage += engine.BULLET_DAMAGE_DELTA if hasattr(engine, 'BULLET_DAMAGE_DELTA') else 1
    from engine.render import spawn_upgrade_particles as _sup
    _sup(engine, t['pos'])
    _sup(engine, t['pos'])
