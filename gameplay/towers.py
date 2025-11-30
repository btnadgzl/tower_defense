import math
from core.events import Event, EVENT_TOWER_FIRE

def update_towers(engine, dt_ms):
    for tower in engine.towers:
        tower['cooldown'] = max(0, tower['cooldown'] - dt_ms)
        if engine.auto_fire and tower['cooldown'] == 0 and engine.enemies:
            target = engine.find_target(tower)
            if target:
                bx, by = tower['pos']
                engine.bullets.append({'pos': [float(bx), float(by)], 'target': target, 'speed': engine.bullet_speed})
                tower['cooldown'] = tower['fire_rate']
                pitch = 1.0 + max(0, (500 - tower['fire_rate'])) / 500.0 * 0.5
                engine.ev_manager.post(Event(EVENT_TOWER_FIRE, data={'pos': tuple(target['pos']), 'pitch': pitch}))
                engine.spawn_muzzle_flash((bx, by))
                engine.trigger_shake(strength=1.2, duration_ms=100)

def find_target(engine, tower):
    tx, ty = tower['pos']
    best = None
    best_dist = float('inf')
    for enemy in engine.enemies:
        ex, ey = enemy['pos']
        d = math.hypot(ex - tx, ey - ty)
        if d <= tower['range'] and d < best_dist:
            best = enemy
            best_dist = d
    return best

def select_tower(engine, pos):
    best_i = None
    best_d = float('inf')
    for i, t in enumerate(engine.towers):
        d = math.hypot(pos[0] - t['pos'][0], pos[1] - t['pos'][1])
        if d < 24 and d < best_d:
            best_d = d
            best_i = i
    engine.selected_tower_idx = best_i

def manual_fire(engine):
    if not engine.towers:
        return
    idx = engine.selected_tower_idx if (engine.selected_tower_idx is not None and 0 <= engine.selected_tower_idx < len(engine.towers)) else 0
    t = engine.towers[idx]
    if t['cooldown'] > 0:
        return
    target = find_target(engine, t)
    if not target:
        return
    bx, by = t['pos']
    engine.bullets.append({'pos': [float(bx), float(by)], 'target': target, 'speed': engine.bullet_speed})
    t['cooldown'] = t['fire_rate']
    pitch = 1.0 + max(0, (500 - t['fire_rate'])) / 500.0 * 0.5
    engine.ev_manager.post(Event(EVENT_TOWER_FIRE, data={'pos': tuple(target['pos']), 'manual': True, 'pitch': pitch}))
    engine.spawn_muzzle_flash((bx, by))
    engine.trigger_shake(strength=1.5, duration_ms=120)
