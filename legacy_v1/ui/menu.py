import pygame
from typing import Any, Tuple
from core.events import Event, EVENT_UI_HOVER, EVENT_UI_CLICK, EVENT_QUIT

def draw_menu(engine: Any) -> None:
    if engine.main_menu_img:
        engine.screen.blit(engine.main_menu_img, (0, 0))
    s = getattr(engine, 'ui_scale', 1.0)
    pb_w = int(200 * s); pb_h = int(80 * s)
    sb_w = int(200 * s); sb_h = int(80 * s)
    eb_w = int(200 * s); eb_h = int(80 * s)
    if engine.playbutton_img:
        pb_w, pb_h = engine.playbutton_img.get_width(), engine.playbutton_img.get_height()
    if engine.setting_button_img:
        sb_w, sb_h = engine.setting_button_img.get_width(), engine.setting_button_img.get_height()
    if engine.exit_menu_img:
        eb_w, eb_h = engine.exit_menu_img.get_width(), engine.exit_menu_img.get_height()
    engine.start_btn_rect = pygame.Rect(0, 0, pb_w, pb_h)
    engine.settings_btn_rect = pygame.Rect(0, 0, sb_w, sb_h)
    engine.exit_menu_btn_rect = pygame.Rect(0, 0, eb_w, eb_h)
    sx = int(engine.width * engine.menu_btn_pos['start'][0]); sy = int(engine.height * engine.menu_btn_pos['start'][1])
    kx = int(engine.width * engine.menu_btn_pos['settings'][0]); ky = int(engine.height * engine.menu_btn_pos['settings'][1])
    ex = int(engine.width * engine.menu_btn_pos['exit'][0]); ey = int(engine.height * engine.menu_btn_pos['exit'][1])
    engine.start_btn_rect.center = (sx, sy)
    engine.settings_btn_rect.center = (kx, ky)
    engine.exit_menu_btn_rect.center = (ex, ey)
    # Resize debug: apply width/height scale if enabled (preserve centers)
    if hasattr(engine, 'menu_btn_scale'):
        sw, sh = engine.menu_btn_scale.get('start', (1.0, 1.0))
        kw, kh = engine.menu_btn_scale.get('settings', (1.0, 1.0))
        ew, eh = engine.menu_btn_scale.get('exit', (1.0, 1.0))
        c1 = engine.start_btn_rect.center
        engine.start_btn_rect.width = max(8, int(engine.start_btn_rect.width * sw))
        engine.start_btn_rect.height = max(8, int(engine.start_btn_rect.height * sh))
        engine.start_btn_rect.center = c1
        c2 = engine.settings_btn_rect.center
        engine.settings_btn_rect.width = max(8, int(engine.settings_btn_rect.width * kw))
        engine.settings_btn_rect.height = max(8, int(engine.settings_btn_rect.height * kh))
        engine.settings_btn_rect.center = c2
        c3 = engine.exit_menu_btn_rect.center
        engine.exit_menu_btn_rect.width = max(8, int(engine.exit_menu_btn_rect.width * ew))
        engine.exit_menu_btn_rect.height = max(8, int(engine.exit_menu_btn_rect.height * eh))
        engine.exit_menu_btn_rect.center = c3
    if engine.playbutton_img:
        engine.screen.blit(engine.playbutton_img, engine.start_btn_rect)
    if engine.setting_button_img:
        engine.screen.blit(engine.setting_button_img, engine.settings_btn_rect)
    if engine.exit_menu_img:
        engine.screen.blit(engine.exit_menu_img, engine.exit_menu_btn_rect)
    if getattr(engine, 'menu_debug', False):
        pygame.draw.rect(engine.screen, (0,200,255), engine.start_btn_rect, 2)
        pygame.draw.rect(engine.screen, (0,200,255), engine.settings_btn_rect, 2)
        pygame.draw.rect(engine.screen, (0,200,255), engine.exit_menu_btn_rect, 2)

    mx, my = pygame.mouse.get_pos()
    prev = getattr(engine, '_menu_hover_id', None)
    cur = None
    if engine.start_btn_rect.collidepoint(mx, my):
        cur = 'start'
    elif engine.settings_btn_rect.collidepoint(mx, my):
        cur = 'settings'
    elif engine.exit_menu_btn_rect.collidepoint(mx, my):
        cur = 'exit'
    pressed = pygame.mouse.get_pressed()[0]
    if not pressed and cur and cur != prev:
        now = pygame.time.get_ticks()
        last = getattr(engine, '_menu_hover_last_ms', 0)
        if now - last >= 180:
            engine._menu_hover_last_ms = now
            engine.ev_manager.post(Event(EVENT_UI_HOVER, data={'id': f'menu:{cur}'}))
    engine._menu_hover_id = cur

def handle_menu_click(engine: Any, pos: Tuple[int, int]) -> None:
    if getattr(engine, 'start_btn_rect', None) and engine.start_btn_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'menu:start'}))
        engine.reset_game()
        engine.elapsed_ms = 0; engine.spawn_ms = 0
        engine.start_transition('playing', style='slide', dir=1)
    elif getattr(engine, 'settings_btn_rect', None) and engine.settings_btn_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'menu:settings'}))
        engine.settings_return_state = 'menu'
        engine.start_transition('settings', style='slide', dir=1)
    elif getattr(engine, 'exit_menu_btn_rect', None) and engine.exit_menu_btn_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'menu:exit'}))
        engine.ev_manager.post(Event(EVENT_QUIT))
