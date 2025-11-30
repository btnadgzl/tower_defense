import math
from core.events import Event, EVENT_ENEMY_KILLED

def update_bullets(engine, dt_ms):
    for bullet in list(engine.bullets):
        tgt = bullet['target']
        if tgt not in engine.enemies:
            engine.bullets.remove(bullet); continue
        dx = tgt['pos'][0] - bullet['pos'][0]; dy = tgt['pos'][1] - bullet['pos'][1]
        dist = math.hypot(dx, dy)
        if dist < 16:
            engine.bullets.remove(bullet)
            tgt['hp'] -= engine.bullet_damage
            if tgt['hp'] <= 0:
                if tgt in engine.enemies:
                    engine.enemies.remove(tgt)
                engine.ev_manager.post(Event(EVENT_ENEMY_KILLED, data={'score': 50, 'coins': 5, 'pos': tuple(tgt['pos'])}))
            continue
        if dist > 0:
            bullet['pos'][0] += (dx / dist) * bullet['speed'] * (dt_ms / 1000.0)
            bullet['pos'][1] += (dy / dist) * bullet['speed'] * (dt_ms / 1000.0)
            engine.particles.append({'pos': [float(bullet['pos'][0]), float(bullet['pos'][1])], 'vel': [0.0, 0.0], 'ttl': 160, 'kind': 'trail', 'radius': 2})
