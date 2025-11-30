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
    hb_rect = pygame.Rect(int(10 * s), int(10 * s), int(150 * s), int(75 * s))
    cb_rect = pygame.Rect(int(170 * s), int(10 * s), int(150 * s), int(75 * s))
    en_rect = pygame.Rect(int(370 * s), int(10 * s), int(150 * s), int(75 * s))
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
        margin = int(6 * s)
        max_w = cb_rect.x - margin - hb_rect.x
        desired_w = hb_rect.width + int(12 * s)
        target_w = max(hb_rect.width, min(desired_w, max_w))
        target_h = hb_rect.height
        scaled = pygame.transform.smoothscale(hb_img, (target_w, target_h))
        engine.screen.blit(scaled, (hb_rect.x, hb_rect.y))
    else:
        pygame.draw.rect(engine.screen, (180, 60, 60), hb_rect)
    if engine.coinbar_img:
        r = engine.coinbar_img.get_rect(center=cb_rect.center)
        engine.screen.blit(engine.coinbar_img, r)
    else:
        pygame.draw.rect(engine.screen, (220, 180, 80), cb_rect)
    if engine.enemies_counter_img:
        r = engine.enemies_counter_img.get_rect(center=en_rect.center)
        engine.screen.blit(engine.enemies_counter_img, r)
    else:
        pygame.draw.rect(engine.screen, (120, 120, 120), en_rect)
    coin_font = engine.counter_font or engine.font
    coin_val = str(engine.coins)
    _draw_text_shadow(engine.screen, coin_font, coin_val, (240, 240, 240), align='center', pos=cb_rect.center)
    enemies_font = engine.counter_font or engine.font
    enemies_val = str(len(engine.enemies))
    _draw_text_shadow(engine.screen, enemies_font, enemies_val, (240, 240, 240), align='midleft', pos=(en_rect.right + int(8 * s), en_rect.centery))
    if engine.state in ('playing','paused'):
        wave = 1 + int(engine.elapsed_ms / 20000)
        wtext = f"Wave {wave}"
        wave_font = engine.counter_font or engine.font
        wrect = wave_font.render(wtext, True, (220, 220, 220)).get_rect(midleft=(cb_rect.right + int(40 * s), cb_rect.centery))
        if wrect.right > en_rect.x - int(6 * s):
            wrect.x = en_rect.x - int(6 * s) - wrect.width
        _draw_text_shadow(engine.screen, wave_font, wtext, (220, 220, 220), rect=wrect)
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
