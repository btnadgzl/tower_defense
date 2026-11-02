import math
from typing import Any
from core.events import Event, EVENT_ENEMY_KILLED

def update_bullets(engine: Any, dt_ms: int) -> None:
    for bullet in list(engine.bullets):
        tgt = bullet['target']
        if tgt not in engine.enemies:
            engine.bullets.remove(bullet)
            if getattr(engine, 'bullet_pool', None):
                engine.bullet_pool.release(bullet)
            continue
        dx = tgt['pos'][0] - bullet['pos'][0]; dy = tgt['pos'][1] - bullet['pos'][1]
        dist = math.hypot(dx, dy)
        if dist < 16:
            engine.bullets.remove(bullet)
            if getattr(engine, 'bullet_pool', None):
                engine.bullet_pool.release(bullet)
            tgt['hp'] -= engine.bullet_damage
            if tgt['hp'] <= 0:
                if tgt in engine.enemies:
                    engine.enemies.remove(tgt)
                coins = 10 if tgt.get('boss') else 5
                engine.ev_manager.post(Event(EVENT_ENEMY_KILLED, data={'score': 50, 'coins': coins, 'pos': tuple(tgt['pos'])}))
            continue
        if dist > 0:
            bullet['pos'][0] += (dx / dist) * bullet['speed'] * (dt_ms / 1000.0)
            bullet['pos'][1] += (dy / dist) * bullet['speed'] * (dt_ms / 1000.0)
            engine.particles.append({'pos': [float(bullet['pos'][0]), float(bullet['pos'][1])], 'vel': [0.0, 0.0], 'ttl': 160, 'kind': 'trail', 'radius': 2})
