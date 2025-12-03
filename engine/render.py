import pygame
import math
import random
from typing import Any

def draw_background(engine: Any) -> None:
    if engine.map_img:
        engine.screen.blit(engine.map_img, engine.camera_offset)
        t = getattr(engine, 'elapsed_ms', 0)
        s = getattr(engine, 'ui_scale', 1.0)
        a1 = 22
        a2 = 16
        off1 = int((t * 0.03) % (engine.width + 1))
        off2 = int((t * 0.018) % (engine.width + 1))
        r1 = pygame.Rect(-off1, int(engine.height * 0.20), engine.width, int(18 * s))
        r2 = pygame.Rect(-off2, int(engine.height * 0.70), engine.width, int(14 * s))
        overlay = pygame.Surface((engine.width, engine.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (20, 20, 30, a1), r1)
        pygame.draw.rect(overlay, (15, 15, 25, a2), r2)
        engine.screen.blit(overlay, (0, 0))
    else:
        engine.screen.fill((30, 30, 30))
        for x in range(0, engine.width, engine.cell):
            pygame.draw.line(engine.screen, (45, 45, 45), (x, 0), (x, engine.height))
        for y in range(0, engine.height, engine.cell):
            pygame.draw.line(engine.screen, (45, 45, 45), (0, y), (engine.width, y))

def draw_towers(engine: Any) -> None:
    ox, oy = engine.camera_offset
    for i, tower in enumerate(engine.towers):
        cx, cy = tower['pos'][0] + ox, tower['pos'][1] + oy
        
        # Check for Tower Fall Animation
        if getattr(engine, 'tower_fall_active', False) and i == 0:
             # Update Animation Timer
             dt = getattr(engine, 'last_dt_ms', 16)
             engine.tower_fall_anim_timer += dt
             
             frames = getattr(engine, 'tower_fallen_frames', [])
             if frames:
                 # 120ms per frame
                 idx = int(engine.tower_fall_anim_timer / 120)
                 idx = min(idx, len(frames) - 1)
                 
                 frame = frames[idx]
                 rect = frame.get_rect(center=(cx, cy))
                 engine.screen.blit(frame, rect)
                 continue # Skip drawing normal tower

        sh = pygame.Surface((60, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 70), (0, 0, 60, 28))
        engine.screen.blit(sh, (int(cx - 30), int(cy + 16)))
        
        # Determine which tower image to use (normal or damaged)
        current_tower_img = engine.tower_img
        
        # Calculate damage level (1-5) if damaged
        if engine.tower_hp_max > 0 and engine.tower_hp < engine.tower_hp_max:
            dmg_imgs = getattr(engine, 'tower_damaged_imgs', [])
            if dmg_imgs:
                # Inverse percentage: 1.0 is full health, 0.0 is dead
                pct = max(0.0, engine.tower_hp / float(engine.tower_hp_max))
                # We have 5 stages. 
                # Stage 1: < 100%
                # Stage 2: < 80%
                # Stage 3: < 60%
                # Stage 4: < 40%
                # Stage 5: < 20%
                # Let's map (1.0 - pct) to index 0..4
                damage_stage = int((1.0 - pct) * 5)
                # Clamp to 0..4 (indices for damaged1..damaged5)
                # Note: damage_stage 0 means slight damage (tower_damaged1)
                damage_stage = max(0, min(len(dmg_imgs) - 1, damage_stage))
                
                # Only use damaged image if actually damaged significantly or just starting
                if pct < 0.99:
                    current_tower_img = dmg_imgs[damage_stage]
                    # Resize if needed (lazy resize, better to do in loader but this is safe)
                    if current_tower_img.get_size() != (engine.tower_img.get_width(), engine.tower_img.get_height()):
                         current_tower_img = pygame.transform.smoothscale(current_tower_img, (engine.tower_img.get_width(), engine.tower_img.get_height()))

        if current_tower_img:
            rect = current_tower_img.get_rect(center=(cx, cy))
            engine.screen.blit(current_tower_img, rect)
        else:
            pygame.draw.circle(engine.screen, (80, 200, 120), (int(cx), int(cy)), 12)
        if engine.selected_tower_idx == i:
            rng = int(tower.get('range', 120))
            pygame.draw.circle(engine.screen, (60, 60, 60), (int(cx), int(cy)), rng, 1)

def draw_enemies(engine: Any) -> None:
    ox, oy = engine.camera_offset
    for enemy in engine.enemies:
        cx, cy = int(enemy['pos'][0] + ox), int(enemy['pos'][1] + oy)
        w = 44 if not enemy.get('boss') else 64
        h = 18 if not enemy.get('boss') else 22
        sh = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 60), (0, 0, w, h))
        engine.screen.blit(sh, (cx - w//2, cy + 12))
        frames = None
        if enemy.get('boss') and getattr(engine, 'boss_frames', None):
            frames = engine.boss_frames
        else:
            frames = engine.enemy_attack_frames if enemy.get('attacking') else engine.enemy_walk_frames
        if frames:
            idx = enemy.get('anim_index', 0) % len(frames)
            frame = frames[idx]
            rect = frame.get_rect(center=(cx, cy))
            engine.screen.blit(frame, rect)
        elif engine.enemy_img:
            rect = engine.enemy_img.get_rect(center=(cx, cy))
            engine.screen.blit(engine.enemy_img, rect)
        else:
            pygame.draw.circle(engine.screen, (220, 80, 80), (cx, cy), 10)
        if enemy.get('boss'):
            btxt = engine.font.render("BOSS", True, (240, 200, 200))
            engine.screen.blit(btxt, (cx - 20, cy - 50))
        maxw = 40
        bw = int(maxw * (enemy['hp'] / float(enemy.get('hp_max', enemy['hp']))))
        barbg = pygame.Rect(cx - maxw//2, cy - 26, maxw, 6)
        pygame.draw.rect(engine.screen, (80, 30, 30), barbg)
        barfg = pygame.Rect(cx - maxw//2, cy - 26, bw, 6)
        color = (30, 200, 80) if not enemy.get('boss') else (220, 60, 60)
        pygame.draw.rect(engine.screen, color, barfg)

def draw_bullets(engine: Any) -> None:
    ox, oy = engine.camera_offset
    for bullet in engine.bullets:
        cx, cy = int(bullet['pos'][0] + ox), int(bullet['pos'][1] + oy)
        if engine.bullet_img:
            rect = engine.bullet_img.get_rect(center=(cx, cy))
            engine.screen.blit(engine.bullet_img, rect)
        else:
            pygame.draw.circle(engine.screen, (240, 220, 80), (cx, cy), 5)
    draw_particles(engine)

def _build_vignette(engine):
    surf = pygame.Surface((engine.width, engine.height), pygame.SRCALPHA)
    cx, cy = engine.width // 2, engine.height // 2
    max_r = int((engine.width + engine.height) * 0.6)
    steps = 24
    for i in range(steps):
        p = i / float(steps - 1)
        r = int(max_r * (0.55 + 0.45 * p))
        alpha = int(10 + 140 * p)
        col = (0, 0, 0, alpha)
        pygame.draw.circle(surf, col, (cx, cy), r)
    engine.vignette_surf = surf

def draw_vignette(engine: Any) -> None:
    if engine.state != 'playing':
        return
    if not hasattr(engine, 'vignette_surf') or engine.vignette_surf is None or engine.vignette_surf.get_size() != (engine.width, engine.height):
        _build_vignette(engine)
    boss_intensity = min(1.0, getattr(engine, 'boss_alert_ms', 0) / 400.0)
    strength = max(0.0, min(1.0, 0.10 + boss_intensity * 0.40))
    alpha = int(255 * strength)
    if alpha <= 0:
        return
    s = engine.vignette_surf.copy()
    s.set_alpha(alpha)
    engine.screen.blit(s, (0, 0))

def _ease_in_out(p: float) -> float:
    return p*p*(3 - 2*p)

def draw_letterbox_boss(engine: Any) -> None:
    if engine.state != 'playing' or engine.boss_banner_ms <= 0:
        return
    dur = 3500.0
    p = max(0.0, min(1.0, 1.0 - engine.boss_banner_ms / dur))
    msg = "BOSS WAVE!!"
    base = engine.font_big.render(msg, True, (240, 220, 220))
    tw, th = base.get_size()
    scale = 1.35
    txt = pygame.transform.smoothscale(base, (int(tw * scale), int(th * scale)))
    tw2, th2 = txt.get_size()
    x_start = -tw2
    x_end = engine.width + tw2
    tx = int(x_start + (x_end - x_start) * p)
    ty = engine.height // 2
    rect = txt.get_rect(center=(tx, ty))
    engine.screen.blit(txt, rect)

def draw_wave_banner(engine: Any) -> None:
    if engine.state != 'playing' or getattr(engine, 'wave_banner_ms', 0) <= 0:
        return
    dur = 2500.0
    p = max(0.0, min(1.0, 1.0 - engine.wave_banner_ms / dur))
    msg = f"Wave {getattr(engine, 'wave_index', 1)}"
    base = engine.font_big.render(msg, True, (240, 240, 240))
    tw, th = base.get_size()
    scale = 1.2
    txt = pygame.transform.smoothscale(base, (int(tw * scale), int(th * scale)))
    tw2, th2 = txt.get_size()
    x_start = -tw2
    x_end = engine.width + tw2
    tx = int(x_start + (x_end - x_start) * p)
    ty = int(engine.height * 0.20)
    rect = txt.get_rect(center=(tx, ty))
    engine.screen.blit(txt, rect)

def draw_radial_hit_overlay(engine):
    if engine.state != 'playing' or getattr(engine, 'hit_overlay_ms', 0) <= 0:
        return
    cx, cy = (engine.towers[0]['pos'] if engine.towers else (engine.width//2, engine.height//2))
    ox, oy = engine.camera_offset
    cx = int(cx + ox); cy = int(cy + oy)
    # intensity
    t = max(0.0, min(1.0, engine.hit_overlay_ms / 180.0))
    max_r = int(140 * getattr(engine, 'ui_scale', 1.0))
    steps = 6
    for i in range(steps):
        p = i / float(steps)
        r = int(max_r * (0.25 + 0.75 * p))
        a = int(80 * (1.0 - p) * t)
        col = (200, 40, 40, a)
        surf = pygame.Surface((engine.width, engine.height), pygame.SRCALPHA)
        pygame.draw.circle(surf, col, (cx, cy), r)
        engine.screen.blit(surf, (0, 0))

def draw_particles(engine):
    ox, oy = engine.camera_offset
    for p in engine.particles:
        ttl_ref = 400.0 if p.get('kind') != 'flash' else 140.0
        life = max(0.0, min(1.0, p.get('ttl', ttl_ref) / ttl_ref))
        kind = p.get('kind')
        if kind == 'flash':
            col = (int(255 * life), int(240 * life), int(160 * life))
        elif kind == 'trail':
            col = (int(255 * life), int(245 * life), int(120 * life))
        elif kind == 'upgrade':
            col = (int(160 * life), int(255 * life), int(160 * life))
        elif kind == 'ui_coin':
            col = (int(255 * life), int(215 * life), int(0 * life))
        elif kind == 'wind':
            col = (int(200 * life), int(255 * life), int(255 * life))
        else:
            col = (int(240 * life), int(200 * life), int(80 * life))
        rad = int(p.get('radius', 3) * (0.7 + 0.3 * life))
        px, py = int(p['pos'][0] + ox), int(p['pos'][1] + oy)
        if kind == 'flash':
            s = pygame.Surface((rad*4, rad*4), pygame.SRCALPHA)
            center = (rad*2, rad*2)
            pygame.draw.circle(s, (col[0], col[1], col[2], int(150 * life)), center, int(rad*1.8))
            pygame.draw.circle(s, (col[0], col[1], col[2], int(220 * life)), center, int(rad*1.0))
            engine.screen.blit(s, (px - rad*2, py - rad*2))
        elif kind == 'wind':
            # Draw a line or elongated ellipse for wind
            vx, vy = p.get('vel', [0,0])
            speed = math.hypot(vx, vy)
            if speed > 0:
                ex = px - (vx/speed) * rad * 4
                ey = py - (vy/speed) * rad * 4
                pygame.draw.line(engine.screen, col, (px, py), (ex, ey), max(1, int(rad/2)))
        else:
            pygame.draw.circle(engine.screen, col, (px, py), max(1, rad))
            
    # Draw Coin Effects (Floating Text + Icon)
    for fx in getattr(engine, 'coin_effects', []):
        fx_pos = fx.get('pos', [0,0])
        px, py = int(fx_pos[0] + ox), int(fx_pos[1] + oy)
        
        # Opacity based on TTL
        ttl_ref = getattr(engine, 'COIN_EFFECT_TTL_MS', 800)
        ttl = fx.get('ttl', 0)
        alpha = max(0, min(255, int(255 * (ttl / ttl_ref))))
        
        # Amount text
        amount = fx.get('amount', 5)
        txt_str = f"+{amount}"
        
        # Font & Color
        font = engine.font  # Use slightly larger font
        color = (255, 215, 0) # Gold
        
        # Render Text
        txt_surf = font.render(txt_str, True, color)
        txt_surf.set_alpha(alpha)
        
        # Icon
        icon = getattr(engine, 'coin_img', None)
        if icon:
             # Scale icon if needed (Larger size)
             iw, ih = 24, 24
             scaled_icon = pygame.transform.smoothscale(icon, (iw, ih))
             scaled_icon.set_alpha(alpha)
             
             # Position: Icon left, Text right
             total_w = iw + 6 + txt_surf.get_width()
             start_x = px - total_w // 2
             
             engine.screen.blit(scaled_icon, (start_x, py - ih//2))
             engine.screen.blit(txt_surf, (start_x + iw + 6, py - txt_surf.get_height()//2))
        else:
             # Just text centered
             rect = txt_surf.get_rect(center=(px, py))
             engine.screen.blit(txt_surf, rect)

def update_particles(engine, dt_ms):
    for p in list(engine.particles):
        p['ttl'] -= dt_ms
        vx, vy = p.get('vel', [0.0, 0.0])
        p['pos'][0] += vx * dt_ms
        p['pos'][1] += vy * dt_ms
        if p['ttl'] <= 0:
            engine.particles.remove(p)

def update_camera_shake(engine, dt_ms):
    if engine.shake_timer > 0:
        engine.shake_timer = max(0, engine.shake_timer - dt_ms)
    else:
        engine.shake_strength = max(0.0, engine.shake_strength - dt_ms * engine.shake_decay)
    if engine.shake_strength > 0.0:
        rx = random.uniform(-1.0, 1.0) * engine.shake_strength
        ry = random.uniform(-1.0, 1.0) * engine.shake_strength
        engine.camera_offset = (int(rx), int(ry))
    else:
        engine.camera_offset = (0, 0)

def trigger_shake(engine, strength=2.0, duration_ms=150):
    engine.shake_strength = max(engine.shake_strength, float(strength))
    engine.shake_timer = max(engine.shake_timer, int(duration_ms))

def spawn_hit_particles(engine, pos, count=12):
    x, y = float(pos[0]), float(pos[1])
    for _ in range(count):
        ang = random.uniform(0.0, math.tau)
        spd = random.uniform(0.08, 0.22)
        vx = math.cos(ang) * spd
        vy = math.sin(ang) * spd
        engine.particles.append({'pos': [x, y], 'vel': [vx, vy], 'ttl': 400, 'kind': 'hit', 'radius': 3})

def spawn_muzzle_flash(engine, pos, count=8):
    x, y = float(pos[0]), float(pos[1])
    for _ in range(count):
        ang = random.uniform(0.0, math.tau)
        spd = random.uniform(0.02, 0.06)
        vx = math.cos(ang) * spd
        vy = math.sin(ang) * spd
        engine.particles.append({'pos': [x, y], 'vel': [vx, vy], 'ttl': 140, 'kind': 'flash', 'radius': 5})

def spawn_upgrade_particles(engine, pos, count=10):
    x, y = float(pos[0]), float(pos[1])
    for _ in range(count):
        ang = random.uniform(0.0, math.tau)
        spd = random.uniform(0.04, 0.10)
        vx = math.cos(ang) * spd
        vy = math.sin(ang) * spd
        engine.particles.append({'pos': [x, y], 'vel': [vx, vy], 'ttl': 300, 'kind': 'upgrade', 'radius': 4})

def spawn_coin_ui_particles(engine, count=8):
    rect = pygame.Rect(170, 10, 150, 75)
    cx, cy = rect.center
    x, y = float(cx), float(cy)
    for _ in range(count):
        ang = random.uniform(0.0, math.tau)
        spd = random.uniform(0.02, 0.06)
        vx = math.cos(ang) * spd
        vy = math.sin(ang) * spd
        engine.particles.append({'pos': [x, y], 'vel': [vx, vy], 'ttl': 220, 'kind': 'ui_coin', 'radius': 3})

def update_coin_effects(engine, dt_ms):
    rise = getattr(engine, 'COIN_EFFECT_RISE_SPEED', 0.05)
    for fx in list(engine.coin_effects):
        fx['ttl'] -= dt_ms
        fx['pos'][1] -= rise * dt_ms
        if fx['ttl'] <= 0:
            engine.coin_effects.remove(fx)

def apply_display_mode(engine):
    if engine.fullscreen:
        info = pygame.display.Info()
        engine.width, engine.height = info.current_w, info.current_h
        engine.screen = pygame.display.set_mode((engine.width, engine.height), pygame.FULLSCREEN)
    else:
        engine.width, engine.height = 800, 600
        engine.screen = pygame.display.set_mode((engine.width, engine.height))
    engine.path_y = engine.height // 2
    sx = engine.width / float(engine.base_width)
    sy = engine.height / float(engine.base_height)
    engine.ui_scale = min(sx, sy)
    if engine.map_img:
        engine.map_img = pygame.transform.smoothscale(engine.map_img, (engine.width, engine.height))
    if engine.main_menu_img:
        engine.main_menu_img = pygame.transform.smoothscale(engine.main_menu_img, (engine.width, engine.height))
    if getattr(engine, 'options_menu_img', None):
        engine.options_menu_img = pygame.transform.smoothscale(engine.options_menu_img, (engine.width, engine.height))
    if getattr(engine, 'settings_menu_img', None):
        engine.settings_menu_img = pygame.transform.smoothscale(engine.settings_menu_img, (engine.width, engine.height))
    if getattr(engine, 'game_over_img', None):
        if not hasattr(engine, '_game_over_img_base') and engine.game_over_img:
            engine._game_over_img_base = engine.game_over_img
        if getattr(engine, '_game_over_img_base', None):
            gw, gh = engine._game_over_img_base.get_size()
            max_w = int(engine.width * 0.60)
            max_h = int(engine.height * 0.28)
            if gw > 0 and gh > 0:
                scale = min(max_w / float(gw), max_h / float(gh), 1.0)
                tw = max(1, int(gw * scale))
                th = max(1, int(gh * scale))
                engine.game_over_img = pygame.transform.smoothscale(engine._game_over_img_base, (tw, th))
    if getattr(engine, 'tower_img', None):
        if not hasattr(engine, '_tower_img_base') and engine.tower_img:
            engine._tower_img_base = engine.tower_img
        if getattr(engine, '_tower_img_base', None):
            tw, th = int(engine.BASE_TOWER_SIZE[0] * engine.ui_scale), int(engine.BASE_TOWER_SIZE[1] * engine.ui_scale)
            engine.tower_img = pygame.transform.smoothscale(engine._tower_img_base, (max(16, tw), max(16, th)))
    if getattr(engine, 'enemy_img', None):
        if not hasattr(engine, '_enemy_img_base') and engine.enemy_img:
            engine._enemy_img_base = engine.enemy_img
        if getattr(engine, '_enemy_img_base', None):
            ew, eh = int(engine.BASE_ENEMY_SIZE[0] * engine.ui_scale), int(engine.BASE_ENEMY_SIZE[1] * engine.ui_scale)
            engine.enemy_img = pygame.transform.smoothscale(engine._enemy_img_base, (max(12, ew), max(12, eh)))
    if getattr(engine, 'bullet_img', None):
        if not hasattr(engine, '_bullet_img_base') and engine.bullet_img:
            engine._bullet_img_base = engine.bullet_img
        if getattr(engine, '_bullet_img_base', None):
            sw, sh = int(engine.BASE_BULLET_SIZE[0] * engine.ui_scale), int(engine.BASE_BULLET_SIZE[1] * engine.ui_scale)
            engine.bullet_img = pygame.transform.smoothscale(engine._bullet_img_base, (max(8, sw), max(8, sh)))
    if getattr(engine, 'enemy_walk_frames', None):
        if not hasattr(engine, '_enemy_walk_frames_base'):
            engine._enemy_walk_frames_base = list(engine.enemy_walk_frames)
        if engine._enemy_walk_frames_base:
            ew, eh = int(engine.BASE_ENEMY_SIZE[0] * engine.ui_scale), int(engine.BASE_ENEMY_SIZE[1] * engine.ui_scale)
            engine.enemy_walk_frames = [pygame.transform.smoothscale(fr, (max(12, ew), max(12, eh))) for fr in engine._enemy_walk_frames_base]
    if getattr(engine, 'enemy_attack_frames', None):
        if not hasattr(engine, '_enemy_attack_frames_base'):
            engine._enemy_attack_frames_base = list(engine.enemy_attack_frames)
        if engine._enemy_attack_frames_base:
            ew, eh = int(engine.BASE_ENEMY_SIZE[0] * engine.ui_scale), int(engine.BASE_ENEMY_SIZE[1] * engine.ui_scale)
            engine.enemy_attack_frames = [pygame.transform.smoothscale(fr, (max(12, ew), max(12, eh))) for fr in engine._enemy_attack_frames_base]
    if getattr(engine, 'boss_frames', None):
        if not hasattr(engine, '_boss_frames_base'):
            engine._boss_frames_base = list(engine.boss_frames)
        if engine._boss_frames_base:
            ew, eh = int(engine.BASE_ENEMY_SIZE[0] * engine.ui_scale), int(engine.BASE_ENEMY_SIZE[1] * engine.ui_scale)
            engine.boss_frames = [pygame.transform.smoothscale(fr, (max(12, ew), max(12, eh))) for fr in engine._boss_frames_base]
    if getattr(engine, 'tower_fallen_frames', None):
        if not hasattr(engine, '_tower_fallen_frames_base'):
            engine._tower_fallen_frames_base = list(engine.tower_fallen_frames)
        if engine._tower_fallen_frames_base:
            tw, th = int(engine.BASE_TOWER_SIZE[0] * engine.ui_scale), int(engine.BASE_TOWER_SIZE[1] * engine.ui_scale)
            engine.tower_fallen_frames = [pygame.transform.smoothscale(fr, (max(16, tw), max(16, th))) for fr in engine._tower_fallen_frames_base]

    if getattr(engine, 'healthbar_img', None):
        target = (int(engine.BASE_HUD_SIZE[0] * engine.ui_scale), int(engine.BASE_HUD_SIZE[1] * engine.ui_scale))
        if target[0] > 0 and target[1] > 0:
            engine.healthbar_img = pygame.transform.smoothscale(engine.healthbar_img, target)
    if getattr(engine, 'healthbar_imgs', None):
        target = (int(engine.BASE_HUD_SIZE[0] * engine.ui_scale), int(engine.BASE_HUD_SIZE[1] * engine.ui_scale))
        if not hasattr(engine, '_healthbar_imgs_base'):
            engine._healthbar_imgs_base = list(engine.healthbar_imgs)
        if engine._healthbar_imgs_base and target[0] > 0 and target[1] > 0:
            engine.healthbar_imgs = [pygame.transform.smoothscale(img, target) for img in engine._healthbar_imgs_base]
    if getattr(engine, 'coinbar_img', None):
        target = (int(engine.BASE_HUD_SIZE[0] * engine.ui_scale), int(engine.BASE_HUD_SIZE[1] * engine.ui_scale))
        if target[0] > 0 and target[1] > 0:
            engine.coinbar_img = pygame.transform.smoothscale(engine.coinbar_img, target)
    if getattr(engine, 'enemies_counter_img', None):
        target = (int(engine.BASE_HUD_SIZE[0] * engine.ui_scale), int(engine.BASE_HUD_SIZE[1] * engine.ui_scale))
        if target[0] > 0 and target[1] > 0:
            engine.enemies_counter_img = pygame.transform.smoothscale(engine.enemies_counter_img, target)
    if getattr(engine, 'previous_img', None):
        sz = (max(12, int(engine.BASE_PREV_SIZE[0] * engine.ui_scale)), max(12, int(engine.BASE_PREV_SIZE[1] * engine.ui_scale)))
        engine.previous_img = pygame.transform.smoothscale(engine.previous_img, sz)
    if getattr(engine, 'volume_up_img', None):
        sz = (max(10, int(30 * engine.ui_scale)), max(10, int(30 * engine.ui_scale)))
        engine.volume_up_img = pygame.transform.smoothscale(engine.volume_up_img, sz)
    if getattr(engine, 'volume_down_img', None):
        sz = (max(10, int(30 * engine.ui_scale)), max(10, int(30 * engine.ui_scale)))
        engine.volume_down_img = pygame.transform.smoothscale(engine.volume_down_img, sz)
    if getattr(engine, 'playbutton_img', None):
        sz = (int(220 * engine.ui_scale), int(60 * engine.ui_scale))
        engine.playbutton_img = pygame.transform.smoothscale(engine.playbutton_img, sz)
    if getattr(engine, 'setting_button_img', None):
        sz = (int(220 * engine.ui_scale), int(60 * engine.ui_scale))
        engine.setting_button_img = pygame.transform.smoothscale(engine.setting_button_img, sz)
    if getattr(engine, 'exit_menu_img', None):
        sz = (int(220 * engine.ui_scale), int(60 * engine.ui_scale))
        engine.exit_menu_img = pygame.transform.smoothscale(engine.exit_menu_img, sz)
    engine.vignette_surf = None
    engine.rain_surf = pygame.Surface((engine.width, engine.height), pygame.SRCALPHA)

def update_rain(engine, dt_ms):
    if not getattr(engine, 'rain_enabled', False):
        return
    target = int(300 * getattr(engine, 'rain_intensity', 0.0) * max(0.4, engine.width / 800.0))
    drops = getattr(engine, 'rain_drops', None)
    if drops is None:
        engine.rain_drops = []
        drops = engine.rain_drops
    while len(drops) < target:
        x = random.uniform(0.0, float(engine.width))
        y = random.uniform(-engine.height * 0.2, engine.height * 0.1)
        spd = random.uniform(0.6, 1.1)
        vx = getattr(engine, 'rain_wind', 0.0) * spd
        vy = spd * 1.8
        ln = random.randint(6, 14)
        drops.append({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'len': ln})
    for d in list(drops):
        d['x'] += d['vx'] * dt_ms
        d['y'] += d['vy'] * dt_ms
        if d['y'] - d['len'] > engine.height or d['x'] < -8 or d['x'] > engine.width + 8:
            drops.remove(d)

def draw_rain(engine):
    if not getattr(engine, 'rain_enabled', False):
        return
    if engine.state not in ('playing', 'paused'):
        return
    if not hasattr(engine, 'rain_surf') or engine.rain_surf is None or engine.rain_surf.get_size() != (engine.width, engine.height):
        engine.rain_surf = pygame.Surface((engine.width, engine.height), pygame.SRCALPHA)
    s = engine.rain_surf
    s.fill((0, 0, 0, 0))
    a = int(140 * min(1.0, getattr(engine, 'rain_intensity', 0.0) + 0.2))
    col = (180, 200, 255, a)
    ox, oy = engine.camera_offset
    for d in getattr(engine, 'rain_drops', []):
        x1 = int(d['x'] + ox)
        y1 = int(d['y'] + oy)
        x2 = int(x1 - d['vx'] * 18)
        y2 = int(y1 - d['vy'] * 18)
        pygame.draw.line(s, col, (x1, y1), (x2, y2), 1)
    engine.screen.blit(s, (0, 0))

def draw_kill_shockwaves(engine):
    waves = getattr(engine, 'kill_shockwaves', None)
    if not waves:
        return
    ox, oy = engine.camera_offset
    for w in list(waves):
        w['ttl'] = w.get('ttl', 420) - getattr(engine, 'last_dt_ms', 16)
        p = max(0.0, min(1.0, 1.0 - w['ttl'] / 420.0))
        cx, cy = int(w['pos'][0] + ox), int(w['pos'][1] + oy)
        r = int(24 + 120 * p)
        a = int(140 * (1.0 - p))
        srf = pygame.Surface((engine.width, engine.height), pygame.SRCALPHA)
        pygame.draw.circle(srf, (255, 235, 130, a), (cx, cy), r, width=2)
        engine.screen.blit(srf, (0, 0))
        if w['ttl'] <= 0:
            try:
                waves.remove(w)
            except ValueError:
                pass
