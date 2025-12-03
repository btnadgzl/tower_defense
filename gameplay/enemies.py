import math
import random
from typing import Any
from core.events import Event, EVENT_GAME_OVER, EVENT_BOSS_NEAR, EVENT_ENEMY_SPAWNED, EVENT_ENEMY_KILLED

def update_enemies(engine: Any, dt_ms: int) -> None:
    tx, ty = (engine.towers[0]['pos'] if engine.towers else (engine.width - 40, engine.height//2))
    for enemy in list(engine.enemies): # Use list() to allow modification during iteration if needed
        # Handle knockback if active
        if enemy.get('knockback'):
            k = enemy['knockback']
            k['timer'] -= dt_ms
            if k['timer'] <= 0:
                del enemy['knockback']
            else:
                # Apply knockback velocity
                enemy['pos'][0] += k['vel'][0] * (dt_ms / 1000.0)
                enemy['pos'][1] += k['vel'][1] * (dt_ms / 1000.0)
                # Skip normal movement during knockback
                enemy['attacking'] = False
                enemy['anim'] = 'walk' # or maybe a stunned anim
                continue

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
            # Apply Sword Damage (Thorns) as DPS while in contact
            sword_dmg = getattr(engine, 'sword_damage', 0.0)
            if sword_dmg > 0:
                enemy['hp'] -= sword_dmg * (dt_ms / 1000.0)
                if enemy['hp'] <= 0:
                    if enemy in engine.enemies:
                        engine.enemies.remove(enemy)
                    coins = 10 if enemy.get('boss') else 5
                    engine.ev_manager.post(Event(EVENT_ENEMY_KILLED, data={'score': 50, 'coins': coins, 'pos': tuple(enemy['pos'])}))
                    continue

            # Apply tower damage only on discrete hits (cooldown based)
            enemy['attack_timer'] = enemy.get('attack_timer', 0) + dt_ms
            cd = int(enemy.get('attack_cooldown_ms', 600))
            if enemy['attack_timer'] >= cd:
                enemy['attack_timer'] -= cd
                prev_hp = engine.tower_hp
                engine.tower_hp = max(0.0, engine.tower_hp - enemy['damage'])
                if engine.tower_hp < prev_hp:
                    engine.hit_overlay_ms = max(getattr(engine, 'hit_overlay_ms', 0), 180)
                if engine.tower_hp <= 0 and engine.state != 'game_over':
                    engine.state = 'game_over'
                    engine.boss_alert_ms = 0
                    engine.boss_banner_ms = 0
                    engine.shake_strength = 0.0
                    engine.camera_offset = (0, 0)
                    # Start Tower Fall Animation
                    engine.tower_fall_active = True
                    engine.tower_fall_anim_index = 0
                    engine.tower_fall_anim_timer = 0
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

def enemy_speed_for_time(engine: Any, t_ms: int) -> float:
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

def spawn_params_for_time(engine: Any, t_ms: int):
    base = 1700.0
    dec = min(700.0, t_ms * 0.005)
    interval = int(max(900.0, base - dec))
    max_enemies = 6 + min(6, int(t_ms / 30000))
    return interval, max_enemies

def spawn_enemy(engine: Any, boss: bool = False) -> None:
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
    from engine.factory import create_enemy
    enemy = create_enemy((-30, int(y)), hp=hp, speed=speed, boss=boss)
    enemy['hp_max'] = hp
    enemy['damage'] = damage
    enemy['anim'] = 'walk'
    enemy['attacking'] = False
    enemy['anim_index'] = 0
    enemy['anim_timer'] = 0
    enemy['anim_speed'] = anim_speed
    enemy['attack_timer'] = 0
    enemy['attack_cooldown_ms'] = 600
    engine.enemies.append(enemy)
    try:
        engine.ev_manager.post(Event(EVENT_ENEMY_SPAWNED, data={'boss': boss, 'pos': tuple(enemy['pos'])}))
    except Exception:
        pass

def update_spawn(engine, dt_ms):
    # Wave-based spawning: 30s waves, fixed enemy count per wave.
    # Boss spawns at the end of the wave; during boss phase no normal spawns.
    if not hasattr(engine, 'wave_duration_ms'):
        return
    engine.wave_elapsed_ms += dt_ms

    # Normal enemy spawn only before wave end and while under target
    if not getattr(engine, 'wave_in_boss_phase', False):
        if engine.wave_elapsed_ms < engine.wave_duration_ms and engine.wave_enemies_spawned < engine.wave_enemies_target:
            interval = int(engine.wave_duration_ms / max(1, int(engine.wave_enemies_target)))
            engine.spawn_ms = getattr(engine, 'spawn_ms', 0) + dt_ms
            if engine.spawn_ms >= interval:
                engine.spawn_ms = 0
                spawn_enemy(engine, boss=False)
                engine.wave_enemies_spawned += 1

    # At wave end, spawn boss once and enter boss phase
    if engine.wave_elapsed_ms >= engine.wave_duration_ms and not getattr(engine, 'wave_in_boss_phase', False):
        spawn_enemy(engine, boss=True)
        engine.boss_banner_ms = 2500
        engine.wave_in_boss_phase = True

    # If in boss phase, wait until boss is killed to advance to next wave
    if getattr(engine, 'wave_in_boss_phase', False):
        boss_alive = any(e.get('boss') for e in engine.enemies)
        if not boss_alive:
            engine.wave_index += 1
            engine.wave_enemies_target = engine.wave_enemy_base + (engine.wave_index - 1) * engine.wave_enemy_increment
            engine.wave_enemies_spawned = 0
            engine.wave_elapsed_ms = 0
            engine.wave_in_boss_phase = False
            engine.spawn_ms = 0
            engine.wave_banner_ms = 2500
