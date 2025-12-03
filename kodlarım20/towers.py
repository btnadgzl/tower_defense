import math
from core.events import Event, EVENT_TOWER_FIRE
from typing import Any, Dict

def update_towers(engine: Any, dt_ms: int) -> None:
    for tower in engine.towers:
        tower['cooldown'] = max(0, tower['cooldown'] - dt_ms)
        if engine.auto_fire and tower['cooldown'] == 0 and engine.enemies:
            target = engine.find_target(tower)
            if target:
                bx, by = tower['pos']
                if getattr(engine, 'bullet_pool', None):
                    b = engine.bullet_pool.acquire((bx, by), target, engine.bullet_speed)
                    engine.bullets.append(b)
                else:
                    engine.bullets.append({'pos': [float(bx), float(by)], 'target': target, 'speed': engine.bullet_speed})
                tower['cooldown'] = tower['fire_rate']
                pitch = 1.0 + max(0, (500 - tower['fire_rate'])) / 500.0 * 0.5
                engine.ev_manager.post(Event(EVENT_TOWER_FIRE, data={'pos': tuple(target['pos']), 'pitch': pitch}))
                engine.spawn_muzzle_flash((bx, by))
                engine.trigger_shake(strength=1.2, duration_ms=100)

def find_target(engine: Any, tower: Dict[str, Any]):
    tx, ty = tower['pos']
    rng = float(tower.get('range', 0))
    in_range = []
    for enemy in engine.enemies:
        ex, ey = enemy['pos']
        d = math.hypot(ex - tx, ey - ty)
        if d <= rng:
            in_range.append(enemy)
    strat = getattr(engine, 'target_strategy', None)
    if strat:
        return strat.select_target(engine, tower, in_range)
    best = None
    best_dist = float('inf')
    for enemy in in_range:
        ex, ey = enemy['pos']
        d = math.hypot(ex - tx, ey - ty)
        if d < best_dist:
            best = enemy
            best_dist = d
    return best

def select_tower(engine: Any, pos):
    best_i = None
    best_d = float('inf')
    for i, t in enumerate(engine.towers):
        d = math.hypot(pos[0] - t['pos'][0], pos[1] - t['pos'][1])
        if d < 24 and d < best_d:
            best_d = d
            best_i = i
    engine.selected_tower_idx = best_i

def manual_fire(engine: Any) -> None:
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
    if getattr(engine, 'bullet_pool', None):
        b = engine.bullet_pool.acquire((bx, by), target, engine.bullet_speed)
        engine.bullets.append(b)
    else:
        engine.bullets.append({'pos': [float(bx), float(by)], 'target': target, 'speed': engine.bullet_speed})
    t['cooldown'] = t['fire_rate']
    pitch = 1.0 + max(0, (500 - t['fire_rate'])) / 500.0 * 0.5
    engine.ev_manager.post(Event(EVENT_TOWER_FIRE, data={'pos': tuple(target['pos']), 'manual': True, 'pitch': pitch}))
    engine.spawn_muzzle_flash((bx, by))
    engine.trigger_shake(strength=1.5, duration_ms=120)
