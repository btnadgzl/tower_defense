import math
import random
from core.events import Event, EVENT_GAME_OVER, EVENT_BOSS_NEAR, EVENT_ENEMY_SPAWNED

def update_enemies(engine, dt_ms):
    tx, ty = (engine.towers[0]['pos'] if engine.towers else (engine.width - 40, engine.height//2))
    for enemy in engine.enemies:
        dx = tx - enemy['pos'][0]; dy = ty - enemy['pos'][1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            enemy['pos'][0] += (dx / dist) * enemy['speed'] * (dt_ms / 1000.0)
            enemy['pos'][1] += (dy / dist) * enemy['speed'] * (dt_ms / 1000.0)
        enemy['attacking'] = dist < 40
        enemy['anim'] = 'attack' if enemy['attacking'] else 'walk'
        enemy['anim_timer'] += dt_ms
        frames_len = len(engine.enemy_attack_frames if enemy['attacking'] else engine.enemy_walk_frames)
        if frames_len > 0 and enemy['anim_timer'] >= enemy.get('anim_speed', 100):
            enemy['anim_timer'] = 0
            enemy['anim_index'] = (enemy.get('anim_index', 0) + 1) % frames_len
        if enemy['attacking']:
            prev_hp = engine.tower_hp
            engine.tower_hp = max(0.0, engine.tower_hp - enemy['damage'] * (dt_ms / 1000.0))
            if engine.tower_hp < prev_hp:
                engine.hit_overlay_ms = max(getattr(engine, 'hit_overlay_ms', 0), 180)
            if engine.tower_hp <= 0 and engine.state != 'game_over':
                engine.state = 'game_over'
                engine.boss_alert_ms = 0
                engine.boss_banner_ms = 0
                engine.shake_strength = 0.0
                engine.camera_offset = (0, 0)
                engine.ev_manager.post(Event(EVENT_GAME_OVER))
        if enemy.get('boss') and dist < 160:
            engine.ev_manager.post(Event(EVENT_BOSS_NEAR, data={'dist': dist}))
            engine.boss_alert_ms = 400
        if enemy.get('boss'):
            hp_ratio = enemy['hp'] / float(enemy.get('hp_max', max(1, enemy['hp'])))
            phase = enemy.get('phase', 0)
            if hp_ratio < 0.66 and phase < 1:
                enemy['speed'] *= 1.15
                enemy['damage'] *= 1.1
                enemy['anim_speed'] = max(80, enemy.get('anim_speed', 100) - 10)
                enemy['phase'] = 1
            if hp_ratio < 0.33 and phase < 2:
                enemy['speed'] *= 1.15
                enemy['damage'] *= 1.15
                enemy['anim_speed'] = max(70, enemy.get('anim_speed', 100) - 10)
                enemy['phase'] = 2

def enemy_speed_for_time(engine, t_ms):
    table = getattr(engine, 'ENEMY_SPEED_TABLE', [
        (25000, 50.0),
        (50000, 60.0),
        (70000, 70.0),
        (100000, 80.0),
        (125000, 85.0),
        (float('inf'), 90.0),
    ])
    for limit, speed in table:
        if t_ms < limit:
            return speed
    return table[-1][1]

def spawn_params_for_time(engine, t_ms):
    base = 1700.0
    dec = min(700.0, t_ms * 0.005)
    interval = int(max(900.0, base - dec))
    max_enemies = 6 + min(6, int(t_ms / 30000))
    return interval, max_enemies

def spawn_enemy(engine, boss=False):
    band_top = random.uniform(50, engine.height/2 - 90)
    band_bottom = random.uniform(engine.height/2 + 90, engine.height - 50)
    y = random.choice([band_top, band_bottom])
    speed = enemy_speed_for_time(engine, engine.elapsed_ms)
    hp_base = 6
    hp = hp_base + int(engine.elapsed_ms / 45000)
    damage = 6.0
    anim_speed = 100
    if boss:
        speed = max(40.0, speed * 0.8)
        hp += 20 + int(engine.elapsed_ms / 30000)
        damage = 12.0
        anim_speed = 120
    enemy = {'pos': [-30.0, float(y)], 'speed': speed, 'hp': hp, 'hp_max': hp, 'damage': damage, 'anim': 'walk', 'attacking': False, 'anim_index': 0, 'anim_timer': 0, 'anim_speed': anim_speed, 'boss': boss}
    engine.enemies.append(enemy)
    try:
        engine.ev_manager.post(Event(EVENT_ENEMY_SPAWNED, data={'boss': boss, 'pos': tuple(enemy['pos'])}))
    except Exception:
        pass

def update_spawn(engine, dt_ms):
    engine.spawn_ms += dt_ms
    engine.spawn_interval, max_enemies = spawn_params_for_time(engine, engine.elapsed_ms)
    if engine.spawn_ms >= engine.spawn_interval and len(engine.enemies) < max_enemies:
        engine.spawn_ms = 0
        spawn_enemy(engine)
    if engine.elapsed_ms >= engine.next_boss_ms and len(engine.enemies) < max_enemies:
        spawn_enemy(engine, boss=True)
        engine.boss_banner_ms = 2500
        engine.next_boss_ms += engine.boss_interval_ms
