import pygame
from typing import Any, Tuple
from core.events import Event, EVENT_UI_CLICK, EVENT_QUIT

def _ease_out_cubic(p):
    q = 1.0 - p
    return 1.0 - q*q*q

def draw_paused_background_to(engine: Any, surface: pygame.Surface) -> None:
    img = getattr(engine, 'pause_menu_img', None)
    if img:
        bg = pygame.transform.smoothscale(img, (engine.width, engine.height))
        surface.blit(bg, (0, 0))
    else:
        overlay = pygame.Surface((engine.width, engine.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

def draw_paused_controls_to(engine: Any, surface: pygame.Surface) -> None:
    s = getattr(engine, 'ui_scale', 1.0)
    engine.continue_btn_rect = pygame.Rect(0, 0, int(180 * s), int(36 * s))
    engine.settings_paused_rect = pygame.Rect(0, 0, int(180 * s), int(36 * s))
    engine.exit_btn_rect = pygame.Rect(0, 0, int(180 * s), int(36 * s))
    engine.quit_btn_rect = pygame.Rect(0, 0, int(180 * s), int(36 * s))
    pos = getattr(engine, 'paused_btn_pos', {'continue': (0.50, 0.45), 'settings': (0.50, 0.52), 'exit': (0.50, 0.60), 'quit': (0.50, 0.68)})
    engine.continue_btn_rect.center = (int(engine.width * pos['continue'][0]), int(engine.height * pos['continue'][1]))
    engine.settings_paused_rect.center = (int(engine.width * pos['settings'][0]), int(engine.height * pos['settings'][1]))
    engine.exit_btn_rect.center = (int(engine.width * pos['exit'][0]), int(engine.height * pos['exit'][1]))
    engine.quit_btn_rect.center = (int(engine.width * pos['quit'][0]), int(engine.height * pos['quit'][1]))
    if getattr(engine, 'paused_btn_scale', None):
        cw, ch = engine.paused_btn_scale.get('continue', (1.0, 1.0))
        sw, sh = engine.paused_btn_scale.get('settings', (1.0, 1.0))
        ew, eh = engine.paused_btn_scale.get('exit', (1.0, 1.0))
        qw, qh = engine.paused_btn_scale.get('quit', (1.0, 1.0))
        c1 = engine.continue_btn_rect.center
        engine.continue_btn_rect.size = (max(8, int(engine.continue_btn_rect.width * cw)), max(8, int(engine.continue_btn_rect.height * ch)))
        engine.continue_btn_rect.center = c1
        c2 = engine.settings_paused_rect.center
        engine.settings_paused_rect.size = (max(8, int(engine.settings_paused_rect.width * sw)), max(8, int(engine.settings_paused_rect.height * sh)))
        engine.settings_paused_rect.center = c2
        c3 = engine.exit_btn_rect.center
        engine.exit_btn_rect.size = (max(8, int(engine.exit_btn_rect.width * ew)), max(8, int(engine.exit_btn_rect.height * eh)))
        engine.exit_btn_rect.center = c3
        c4 = engine.quit_btn_rect.center
        engine.quit_btn_rect.size = (max(8, int(engine.quit_btn_rect.width * qw)), max(8, int(engine.quit_btn_rect.height * qh)))
        engine.quit_btn_rect.center = c4
    if getattr(engine, 'paused_debug', False):
        pygame.draw.rect(surface, (0,200,255), engine.continue_btn_rect, 2)
        pygame.draw.rect(surface, (0,200,255), engine.settings_paused_rect, 2)
        pygame.draw.rect(surface, (0,200,255), engine.exit_btn_rect, 2)
        pygame.draw.rect(surface, (0,200,255), engine.quit_btn_rect, 2)

def draw_overlays(engine: Any) -> None:
    if engine.state == 'paused':
        draw_paused_background_to(engine, engine.screen)
        draw_paused_controls_to(engine, engine.screen)
    if engine.state == 'game_over':
        if not hasattr(engine, 'go_anim_dur_ms'):
            engine.go_anim_dur_ms = 850.0
        engine.go_anim_p = min(1.0, (getattr(engine, 'go_anim_p', 0.0)) + (getattr(engine, 'last_dt_ms', 16) / float(engine.go_anim_dur_ms)))
        e = _ease_out_cubic(engine.go_anim_p)
        s = getattr(engine, 'ui_scale', 1.0)
        start_y = -int(140 * s)
        overlay = pygame.Surface((engine.width, engine.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        engine.screen.blit(overlay, (0, 0))
        if engine.game_over_img:
            gy_target = int(engine.height * 0.35)
            gy = int(start_y + (gy_target - start_y) * e)
            rect = engine.game_over_img.get_rect(center=(engine.width//2, gy))
            engine.screen.blit(engine.game_over_img, rect)
        rw, rh = 160, 36
        engine.restart_btn_rect = pygame.Rect(0, 0, rw, rh)
        rcx = int(engine.width * engine.go_restart_pos[0]); rcy_target = int(engine.height * engine.go_restart_pos[1])
        rcy = int(start_y + (rcy_target - start_y) * e)
        engine.restart_btn_rect.center = (rcx, rcy)
        pygame.draw.rect(engine.screen, (80, 180, 80), engine.restart_btn_rect)
        pygame.draw.rect(engine.screen, (40, 100, 40), engine.restart_btn_rect, 2)
        txt_btn = engine.font.render("Restart", True, (20, 20, 20))
        engine.screen.blit(txt_btn, txt_btn.get_rect(center=engine.restart_btn_rect.center))
        ew, eh = 160, 36
        if engine.exit_menu_img:
            ew, eh = engine.exit_menu_img.get_width(), engine.exit_menu_img.get_height()
        engine.go_exit_btn_rect = pygame.Rect(0, 0, ew, eh)
        ecx = int(engine.width * engine.go_exit_pos[0]); ecy_target = int(engine.height * engine.go_exit_pos[1])
        ecy = int(start_y + (ecy_target - start_y) * e)
        engine.go_exit_btn_rect.center = (ecx, ecy)
        if engine.exit_menu_img:
            engine.screen.blit(engine.exit_menu_img, engine.go_exit_btn_rect)
        else:
            pygame.draw.rect(engine.screen, (220, 180, 80), engine.go_exit_btn_rect)
            pygame.draw.rect(engine.screen, (140, 120, 40), engine.go_exit_btn_rect, 2)
            e_txt = engine.font.render("Exit to Menu", True, (20, 20, 20))
            engine.screen.blit(e_txt, e_txt.get_rect(center=engine.go_exit_btn_rect.center))
        if getattr(engine, 'go_debug', False):
            pygame.draw.rect(engine.screen, (0,200,255), engine.restart_btn_rect, 2)
            pygame.draw.rect(engine.screen, (0,200,255), engine.go_exit_btn_rect, 2)
    from engine.render import draw_vignette as _v
    _v(engine)
    from engine.render import draw_letterbox_boss as _lb
    _lb(engine)
    from engine.render import draw_wave_banner as _wb
    _wb(engine)
    if engine.state == 'playing' and engine.boss_alert_ms > 0:
        alpha = int(90 * (engine.boss_alert_ms / 400.0))
        overlay = pygame.Surface((engine.width, engine.height), pygame.SRCALPHA)
        overlay.fill((120, 0, 0, max(20, min(120, alpha))))
        engine.screen.blit(overlay, (0, 0))

    from engine.render import draw_radial_hit_overlay as _hit, draw_kill_shockwaves as _shock
    _hit(engine)
    _shock(engine)
    if engine.state == 'playing':
        boss = None
        for e in engine.enemies:
            if e.get('boss'):
                boss = e; break
        if boss:
            ratio = max(0.0, min(1.0, boss['hp'] / float(boss.get('hp_max', boss['hp']))))
            bar = pygame.Rect(engine.width//2 - 200, 10, 400, 12)
            pygame.draw.rect(engine.screen, (60, 20, 20), bar)
            fg = pygame.Rect(bar.x, bar.y, int(bar.width * ratio), bar.height)
            pygame.draw.rect(engine.screen, (220, 60, 60), fg)
            btxt = engine.font.render("BOSS", True, (240, 240, 240))
            engine.screen.blit(btxt, (bar.x + bar.width + 8, bar.y - 4))

def handle_paused_click(engine: Any, pos: Tuple[int, int]) -> None:
    if getattr(engine, 'continue_btn_rect', None) and engine.continue_btn_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'paused:continue'}))
        engine.start_transition('playing', style='zoom')
    elif getattr(engine, 'settings_paused_rect', None) and engine.settings_paused_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'paused:settings'}))
        engine.settings_return_state = 'paused'
        engine.start_transition('settings', style='slide', dir=1)
    elif getattr(engine, 'exit_btn_rect', None) and engine.exit_btn_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'paused:exit_menu'}))
        engine.reset_game()
        engine.start_transition('menu', style='slide', dir=-1)
    elif getattr(engine, 'quit_btn_rect', None) and engine.quit_btn_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'paused:quit'}))
        engine.ev_manager.post(Event(EVENT_QUIT))

def handle_game_over_click(engine: Any, pos: Tuple[int, int]) -> None:
    if getattr(engine, 'restart_btn_rect', None) and engine.restart_btn_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'game_over:restart'}))
        engine.reset_game(); engine.start_transition('playing')
    elif getattr(engine, 'go_exit_btn_rect', None) and engine.go_exit_btn_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'game_over:exit_menu'}))
        engine.reset_game()
        engine.start_transition('menu')
def draw_intro(engine: Any) -> None:
    if not getattr(engine, 'intro_anim_active', False):
        return
    if not getattr(engine, 'intro_anim_started', False):
        engine.intro_anim_start_ms = pygame.time.get_ticks()
        engine.intro_anim_started = True
    dur = float(getattr(engine, 'intro_anim_dur_ms', 700.0))
    ticks = pygame.time.get_ticks()
    start = getattr(engine, 'intro_anim_start_ms', ticks)
    engine.intro_anim_p = min(1.0, (ticks - start) / dur)
    e = _ease_out_cubic(engine.intro_anim_p)
    img = getattr(engine, 'start_icon_img', None)
    if img:
        w, h = img.get_size()
        x_start = -int(w * 1.4)
        x_end = engine.width + int(w * 1.4)
        base_tx = int(x_start + (x_end - x_start) * e)
        ty = engine.height // 2
        scale = max(0.1, 1.0 - 0.28 * e)
        ang = 12.0 * e
        sw = max(1, int(w * scale)); sh = max(1, int(h * scale))
        srf = pygame.transform.smoothscale(img, (sw, sh))
        srf = pygame.transform.rotate(srf, ang)
        a = max(0, min(255, int(255 * (1.0 - e) ** 1.3)))
        srf.set_alpha(a)
        rect = srf.get_rect(center=(base_tx, ty))
        engine.screen.blit(srf, rect)
        for i in range(1, 3):
            p = max(0.0, e - i * 0.08)
            tw = max(1, int(w * max(0.1, 1.0 - 0.28 * p)))
            th = max(1, int(h * max(0.1, 1.0 - 0.28 * p)))
            s2 = pygame.transform.smoothscale(img, (tw, th))
            r2 = pygame.transform.rotate(s2, 12.0 * p)
            a2 = max(0, min(255, int(150 * (1.0 - p) ** 1.5)))
            r2.set_alpha(a2)
            tx2 = int(x_start + (x_end - x_start) * p) - i * 10
            rect2 = r2.get_rect(center=(tx2, ty))
            engine.screen.blit(r2, rect2)
    if engine.intro_anim_p >= 1.0:
        engine.intro_anim_active = False
