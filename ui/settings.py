import pygame
from core.events import Event, EVENT_SOUND_VOLUME_CHANGED, EVENT_UI_CLICK

def draw_settings(engine):
    s = getattr(engine, 'ui_scale', 1.0)
    panel = pygame.Rect(engine.width//2 - int(160 * s), engine.height//2 - int(120 * s), int(320 * s), int(240 * s))
    if getattr(engine, 'options_menu_img', None):
        bg = pygame.transform.smoothscale(engine.options_menu_img, (engine.width, engine.height))
        engine.screen.blit(bg, (0, 0))
    elif getattr(engine, 'settings_menu_img', None):
        bg = pygame.transform.smoothscale(engine.settings_menu_img, (engine.width, engine.height))
        engine.screen.blit(bg, (0, 0))
    else:
        pygame.draw.rect(engine.screen, (20, 20, 20), panel)
        pygame.draw.rect(engine.screen, (90, 90, 90), panel, 2)
    engine.prev_btn_rect = pygame.Rect(int(10 * s), int(10 * s), int(36 * s), int(36 * s))
    if engine.previous_img:
        engine.screen.blit(engine.previous_img, engine.prev_btn_rect)
    else:
        pygame.draw.rect(engine.screen, (200, 200, 200), engine.prev_btn_rect)
    engine.fs_toggle_rect = pygame.Rect(0, 0, int(115 * s), int(74 * s)); engine.fs_toggle_rect.center = (int(406 * s), int(218 * s))
    engine.sound_toggle_rect = pygame.Rect(0, 0, int(115 * s), int(74 * s)); engine.sound_toggle_rect.center = (int(405 * s), int(302 * s))
    engine.options_back_rect = pygame.Rect(0, 0, int(115 * s), int(74 * s)); engine.options_back_rect.center = (int(405 * s), int(388 * s))
    engine.vol_up_rect = pygame.Rect(0, 0, int(50 * s), int(35 * s)); engine.vol_up_rect.center = (int(500 * s), int(292 * s))
    engine.vol_down_rect = pygame.Rect(0, 0, int(50 * s), int(35 * s)); engine.vol_down_rect.center = (int(500 * s), int(332 * s))
    vol_pct = int(round(engine.sound_volume * 100))
    vol_txt = f"Volume: {vol_pct}%"
    color = (121, 62, 16)
    txt_surf = engine.font_big.render(vol_txt, True, color)
    rx = int(engine.width - int(12 * s))
    ry = engine.height // 2 - int(36 * s)
    engine.screen.blit(txt_surf, txt_surf.get_rect(midright=(rx, ry)))

    mx, my = pygame.mouse.get_pos()
    prev = getattr(engine, '_settings_hover_id', None)
    cur = None
    if engine.fs_toggle_rect.collidepoint(mx, my):
        cur = 'fs_toggle'
    elif engine.sound_toggle_rect.collidepoint(mx, my):
        cur = 'sound_toggle'
    elif engine.options_back_rect.collidepoint(mx, my):
        cur = 'back'
    elif engine.vol_up_rect.collidepoint(mx, my):
        cur = 'vol_up'
    elif engine.vol_down_rect.collidepoint(mx, my):
        cur = 'vol_down'
    pressed = pygame.mouse.get_pressed()[0]
    if not pressed and cur and cur != prev:
        now = pygame.time.get_ticks()
        last = getattr(engine, '_settings_hover_last_ms', 0)
        if now - last >= 180:
            engine._settings_hover_last_ms = now
            from core.events import Event, EVENT_UI_HOVER
            engine.ev_manager.post(Event(EVENT_UI_HOVER, data={'id': f'settings:{cur}'}))
    engine._settings_hover_id = cur

def handle_settings_click(engine, pos):
    if getattr(engine, 'prev_btn_rect', None) and engine.prev_btn_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'settings:prev'}))
        target = getattr(engine, 'settings_return_state', None)
        engine.start_transition(target if target in ('menu', 'paused') else 'menu', style='slide', dir=-1)
        engine.settings_return_state = None
    elif getattr(engine, 'options_back_rect', None) and engine.options_back_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'settings:back'}))
        target = getattr(engine, 'settings_return_state', None)
        engine.start_transition(target if target in ('menu', 'paused') else 'menu', style='slide', dir=-1)
        engine.settings_return_state = None
    elif getattr(engine, 'fs_toggle_rect', None) and engine.fs_toggle_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'settings:fullscreen'}))
        engine.fullscreen = not engine.fullscreen
        engine.apply_display_mode()
    elif getattr(engine, 'sound_toggle_rect', None) and engine.sound_toggle_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'settings:sound_toggle'}))
        engine.sound_enabled = not engine.sound_enabled
        engine.ev_manager.post(Event('SoundToggle', data={'enabled': engine.sound_enabled}))
    elif getattr(engine, 'vol_up_rect', None) and engine.vol_up_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'settings:vol_up'}))
        engine.sound_volume = min(1.0, engine.sound_volume + 0.1)
        engine.ev_manager.post(Event(EVENT_SOUND_VOLUME_CHANGED, data={'volume': engine.sound_volume}))
    elif getattr(engine, 'vol_down_rect', None) and engine.vol_down_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'settings:vol_down'}))
        engine.sound_volume = max(0.0, engine.sound_volume - 0.1)
        engine.ev_manager.post(Event(EVENT_SOUND_VOLUME_CHANGED, data={'volume': engine.sound_volume}))
