import pygame

def _draw_text_shadow(screen, font, text, color, rect=None, align='center', pos=None):
    if rect is None:
        rect = font.render(text, True, color).get_rect(**{align: pos})
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        screen.blit(font.render(text, True, (0, 0, 0)), (rect.x + dx, rect.y + dy))
    screen.blit(font.render(text, True, color), rect)
    return rect

def draw_ui(engine):
    s = getattr(engine, 'ui_scale', 1.0)
    hp = getattr(engine, 'hud_pos', {'healthbar': (0.12, 0.10), 'coinbar': (0.32, 0.10), 'enemies': (0.52, 0.10), 'ulti': (0.12, 0.20)})
    hs = getattr(engine, 'hud_scale', {'healthbar': (1.0, 1.0), 'coinbar': (1.0, 1.0), 'enemies': (1.0, 1.0), 'ulti': (1.0, 1.0)})
    bw, bh = int(engine.BASE_HUD_SIZE[0] * s), int(engine.BASE_HUD_SIZE[1] * s)
    hb_rect = pygame.Rect(0, 0, max(8, int(bw * hs['healthbar'][0])), max(8, int(bh * hs['healthbar'][1])))
    cb_rect = pygame.Rect(0, 0, max(8, int(bw * hs['coinbar'][0])), max(8, int(bh * hs['coinbar'][1])))
    en_rect = pygame.Rect(0, 0, max(8, int(bw * hs['enemies'][0])), max(8, int(bh * hs['enemies'][1])))
    hb_rect.center = (int(engine.width * hp['healthbar'][0]), int(engine.height * hp['healthbar'][1]))
    cb_rect.center = (int(engine.width * hp['coinbar'][0]), int(engine.height * hp['coinbar'][1]))
    en_rect.center = (int(engine.width * hp['enemies'][0]), int(engine.height * hp['enemies'][1]))
    hb_img = None
    if getattr(engine, 'healthbar_imgs', None):
        if engine.tower_hp_max > 0:
            pct = max(0.0, min(1.0, engine.tower_hp / float(engine.tower_hp_max)))
        else:
            pct = 1.0
        idx = max(0, min(5, int(round(pct * 5))))
        if len(engine.healthbar_imgs) > idx:
            hb_img = engine.healthbar_imgs[idx]
    elif engine.healthbar_img:
        hb_img = engine.healthbar_img
    if hb_img:
        iw, ih = hb_img.get_width(), hb_img.get_height()
        tw, th = hb_rect.width, hb_rect.height
        img_to_draw = hb_img
        if (tw, th) != (iw, ih):
            img_to_draw = pygame.transform.smoothscale(hb_img, (tw, th))
        engine.screen.blit(img_to_draw, hb_rect)
    else:
        pygame.draw.rect(engine.screen, (180, 60, 60), hb_rect)

    # --- ULTI BAR ---
    ur_w = hb_rect.width
    ur_h = int(20 * s)
    ur_w = max(8, int(ur_w * hs['ulti'][0]))
    ur_h = max(8, int(ur_h * hs['ulti'][1]))
    ur_rect = pygame.Rect(0, 0, ur_w, ur_h)
    ur_rect.center = (int(engine.width * hp['ulti'][0]), int(engine.height * hp['ulti'][1]))
    # Background
    pygame.draw.rect(engine.screen, (30, 30, 30), ur_rect)
    # Fill
    if getattr(engine, 'ulti_max', 0) > 0:
        pct = engine.ulti_charge / float(engine.ulti_max)
        fill_w = int(ur_rect.width * pct)
        fr = pygame.Rect(ur_rect.x, ur_rect.y, fill_w, ur_rect.height)
        # Color: Blue if charging, Flashing Green/Cyan if ready
        ucolor = (0, 150, 255)
        if engine.ulti_charge >= engine.ulti_max:
            # Simple pulse effect
            if (pygame.time.get_ticks() // 200) % 2 == 0:
                ucolor = (100, 255, 100)
            else:
                ucolor = (0, 200, 200)
        pygame.draw.rect(engine.screen, ucolor, fr)
        
        # Border
        pygame.draw.rect(engine.screen, (100, 100, 100), ur_rect, 1)
        
        # Text
        txt_str = "READY (Q)" if engine.ulti_charge >= engine.ulti_max else f"ULTI {engine.ulti_charge}/{engine.ulti_max}"
        _draw_text_shadow(engine.screen, engine.font_small, txt_str, (255,255,255), rect=ur_rect)
    # ----------------

    if engine.coinbar_img:
        img = engine.coinbar_img
        iw, ih = img.get_size()
        tw, th = cb_rect.size
        if (tw, th) != (iw, ih):
            img = pygame.transform.smoothscale(img, (tw, th))
        engine.screen.blit(img, cb_rect)
    else:
        pygame.draw.rect(engine.screen, (220, 180, 80), cb_rect)
    if engine.enemies_counter_img:
        img = engine.enemies_counter_img
        iw, ih = img.get_size()
        tw, th = en_rect.size
        if (tw, th) != (iw, ih):
            img = pygame.transform.smoothscale(img, (tw, th))
        engine.screen.blit(img, en_rect)
    else:
        pygame.draw.rect(engine.screen, (120, 120, 120), en_rect)
    coin_font = engine.counter_font or engine.font
    coin_val = str(engine.coins)
    _draw_text_shadow(engine.screen, coin_font, coin_val, (240, 240, 240), align='midleft', pos=(cb_rect.right + int(8 * s) - 8, cb_rect.centery))
    enemies_font = engine.counter_font or engine.font
    enemies_val = str(len(engine.enemies))
    _draw_text_shadow(engine.screen, enemies_font, enemies_val, (240, 240, 240), align='midleft', pos=(en_rect.right + int(8 * s), en_rect.centery))
    if engine.state in ('playing','paused'):
        wave = getattr(engine, 'wave_index', 1)
        wtext = f"Wave {wave}"
        wave_font = engine.counter_font or engine.font
        if 'wave' in hp:
            wx = int(engine.width * hp['wave'][0]); wy = int(engine.height * hp['wave'][1])
            wrect = wave_font.render(wtext, True, (220, 220, 220)).get_rect(center=(wx, wy))
        else:
            wrect = wave_font.render(wtext, True, (220, 220, 220)).get_rect(midleft=(cb_rect.right + int(40 * s), cb_rect.centery))
        if not getattr(engine, 'hud_debug', False):
            if wrect.right > en_rect.x - int(6 * s):
                wrect.x = en_rect.x - int(6 * s) - wrect.width
        _draw_text_shadow(engine.screen, wave_font, wtext, (220, 220, 220), rect=wrect)
        if getattr(engine, 'hud_debug', False):
            pygame.draw.rect(engine.screen, (0,200,255), wrect, 2)
    if getattr(engine, 'hud_debug', False):
        pygame.draw.rect(engine.screen, (0,200,255), hb_rect, 2)
        pygame.draw.rect(engine.screen, (0,200,255), cb_rect, 2)
        pygame.draw.rect(engine.screen, (0,200,255), en_rect, 2)
        pygame.draw.rect(engine.screen, (255,140,0), ur_rect, 2)
    if engine.state == 'settings':
        from ui.settings import draw_settings
        draw_settings(engine)
    elif engine.state == 'menu':
        engine.draw_menu()
    if engine.upgrade_open or getattr(engine, 'upgrade_anim_running', False):
        engine.draw_upgrade_panel()
    fps = int(engine.clock.get_fps()) if getattr(engine, 'clock', None) else 0
    dt = getattr(engine, 'last_dt_ms', 0)
    txt = f"FPS {fps} | {dt} ms"
    srf = engine.font_small.render(txt, True, (240, 240, 240))
    bg = pygame.Surface((srf.get_width()+8, srf.get_height()+4), pygame.SRCALPHA)
    bg.fill((10, 10, 10, 120))
    rx = engine.width - (srf.get_width()+8) - 8
    ry = 8
    engine.screen.blit(bg, (rx, ry))
    engine.screen.blit(srf, (rx+4, ry+2))
