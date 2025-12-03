import pygame
from typing import Any
from core.events import Event, EVENT_SOUND_VOLUME_CHANGED, EVENT_UI_CLICK, EVENT_SOUND_TOGGLE, EVENT_UI_HOVER

def draw_settings(engine: Any) -> None:
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
    engine.fs_toggle_rect = pygame.Rect(0, 0, int(115 * s), int(74 * s))
    engine.sound_toggle_rect = pygame.Rect(0, 0, int(115 * s), int(74 * s))
    engine.options_back_rect = pygame.Rect(0, 0, int(115 * s), int(74 * s))
    engine.vol_up_rect = pygame.Rect(0, 0, int(50 * s), int(35 * s))
    engine.vol_down_rect = pygame.Rect(0, 0, int(50 * s), int(35 * s))
    pos = getattr(engine, 'settings_btn_pos', {
        'fs_toggle': (406/800.0, 218/600.0),
        'sound_toggle': (405/800.0, 302/600.0),
        'back': (405/800.0, 388/600.0),
        'vol_up': (500/800.0, 292/600.0),
        'vol_down': (500/800.0, 332/600.0),
    })
    engine.fs_toggle_rect.center = (int(engine.width * pos['fs_toggle'][0]), int(engine.height * pos['fs_toggle'][1]))
    engine.sound_toggle_rect.center = (int(engine.width * pos['sound_toggle'][0]), int(engine.height * pos['sound_toggle'][1]))
    engine.options_back_rect.center = (int(engine.width * pos['back'][0]), int(engine.height * pos['back'][1]))
    engine.vol_up_rect.center = (int(engine.width * pos['vol_up'][0]), int(engine.height * pos['vol_up'][1]))
    engine.vol_down_rect.center = (int(engine.width * pos['vol_down'][0]), int(engine.height * pos['vol_down'][1]))
    if hasattr(engine, 'settings_btn_scale'):
        c_fs = engine.fs_toggle_rect.center
        c_sn = engine.sound_toggle_rect.center
        c_bk = engine.options_back_rect.center
        c_vu = engine.vol_up_rect.center
        c_vd = engine.vol_down_rect.center
        fsw, fsh = engine.settings_btn_scale.get('fs_toggle', (1.0, 1.0))
        snw, snh = engine.settings_btn_scale.get('sound_toggle', (1.0, 1.0))
        bkw, bkh = engine.settings_btn_scale.get('back', (1.0, 1.0))
        vuw, vuh = engine.settings_btn_scale.get('vol_up', (1.0, 1.0))
        vdw, vdh = engine.settings_btn_scale.get('vol_down', (1.0, 1.0))
        engine.fs_toggle_rect.size = (max(8, int(engine.fs_toggle_rect.width * fsw)), max(8, int(engine.fs_toggle_rect.height * fsh)))
        engine.sound_toggle_rect.size = (max(8, int(engine.sound_toggle_rect.width * snw)), max(8, int(engine.sound_toggle_rect.height * snh)))
        engine.options_back_rect.size = (max(8, int(engine.options_back_rect.width * bkw)), max(8, int(engine.options_back_rect.height * bkh)))
        engine.vol_up_rect.size = (max(8, int(engine.vol_up_rect.width * vuw)), max(8, int(engine.vol_up_rect.height * vuh)))
        engine.vol_down_rect.size = (max(8, int(engine.vol_down_rect.width * vdw)), max(8, int(engine.vol_down_rect.height * vdh)))
        engine.fs_toggle_rect.center = c_fs
        engine.sound_toggle_rect.center = c_sn
        engine.options_back_rect.center = c_bk
        engine.vol_up_rect.center = c_vu
        engine.vol_down_rect.center = c_vd
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
            engine.ev_manager.post(Event(EVENT_UI_HOVER, data={'id': f'settings:{cur}'}))
    engine._settings_hover_id = cur
    if getattr(engine, 'settings_debug', False):
        pygame.draw.rect(engine.screen, (0,200,255), engine.fs_toggle_rect, 2)
        pygame.draw.rect(engine.screen, (0,200,255), engine.sound_toggle_rect, 2)
        pygame.draw.rect(engine.screen, (0,200,255), engine.options_back_rect, 2)
        pygame.draw.rect(engine.screen, (255,140,0), engine.vol_up_rect, 2)
        pygame.draw.rect(engine.screen, (255,140,0), engine.vol_down_rect, 2)

def handle_settings_click(engine: Any, pos) -> None:
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
        engine.ev_manager.post(Event(EVENT_SOUND_TOGGLE, data={'enabled': engine.sound_enabled}))
    elif getattr(engine, 'vol_up_rect', None) and engine.vol_up_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'settings:vol_up'}))
        engine.sound_volume = min(1.0, engine.sound_volume + 0.1)
        engine.ev_manager.post(Event(EVENT_SOUND_VOLUME_CHANGED, data={'volume': engine.sound_volume}))
    elif getattr(engine, 'vol_down_rect', None) and engine.vol_down_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'settings:vol_down'}))
        engine.sound_volume = max(0.0, engine.sound_volume - 0.1)
        engine.ev_manager.post(Event(EVENT_SOUND_VOLUME_CHANGED, data={'volume': engine.sound_volume}))
