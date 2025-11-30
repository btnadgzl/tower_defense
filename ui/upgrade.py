import pygame
from core.events import Event, EVENT_UPGRADE_TOWER, EVENT_UI_CLICK

def _ease_out_cubic(p):
    q = 1.0 - p
    return 1.0 - q*q*q

def draw_upgrade_panel(engine):
    s = getattr(engine, 'ui_scale', 1.0)
    panel = pygame.Rect(engine.width - int(240 * s), int(50 * s), int(230 * s), int(220 * s))
    desired_open = bool(engine.upgrade_open)
    if not hasattr(engine, 'upgrade_anim_p'):
        engine.upgrade_anim_p = 1.0 if desired_open else 0.0
        engine.upgrade_anim_from = panel.width
        engine.upgrade_anim_to = 0
    if getattr(engine, 'upgrade_anim_target_open', None) != desired_open:
        engine.upgrade_anim_target_open = desired_open
        engine.upgrade_anim_p = 0.0
        cur_off = getattr(engine, 'upgrade_anim_offset', panel.width)
        engine.upgrade_anim_from = cur_off
        engine.upgrade_anim_to = 0 if desired_open else panel.width
        engine.upgrade_anim_delay_left_ms = 100 if desired_open else 0
    dur = 0.45
    dt_ms = getattr(engine, 'last_dt_ms', 16)
    if getattr(engine, 'upgrade_anim_delay_left_ms', 0) > 0:
        engine.upgrade_anim_delay_left_ms = max(0, engine.upgrade_anim_delay_left_ms - dt_ms)
    else:
        dt = dt_ms / 1000.0
        engine.upgrade_anim_p = min(1.0, engine.upgrade_anim_p + dt / dur)
    e = _ease_out_cubic(engine.upgrade_anim_p)
    cur = int(round(engine.upgrade_anim_from + (engine.upgrade_anim_to - engine.upgrade_anim_from) * e))
    engine.upgrade_anim_offset = cur
    engine.upgrade_anim_running = engine.upgrade_anim_p < 1.0
    rect = panel.copy(); rect.x = panel.x + cur
    if engine.upgrademenu_img:
        bg = pygame.transform.smoothscale(engine.upgrademenu_img, (rect.width, rect.height))
        engine.screen.blit(bg, rect)
    else:
        pygame.draw.rect(engine.screen, (20, 20, 20), rect)
        pygame.draw.rect(engine.screen, (90, 90, 90), rect, 2)
    title = engine.font.render("Upgrades", True, (240, 240, 240))
    engine.screen.blit(title, (rect.x + 10, rect.y + 10))
    engine.upgrade_close_rect = pygame.Rect(rect.right - int(28 * s), rect.y + int(8 * s), int(20 * s), int(20 * s))
    if getattr(engine, 'close_img', None):
        engine.screen.blit(engine.close_img, engine.upgrade_close_rect)
    else:
        pygame.draw.rect(engine.screen, (180, 80, 80), engine.upgrade_close_rect)
    coins_txt = engine.font.render(f"Coins: {engine.coins}", True, (240, 240, 240))
    engine.screen.blit(coins_txt, (rect.x + 10, rect.y + 40))
    for btn in engine.get_upgrade_buttons():
        r = btn['rect'].copy(); r.x = btn['rect'].x + int(round(cur))
        pygame.draw.rect(engine.screen, (60, 60, 60), r)
        pygame.draw.rect(engine.screen, (120, 120, 120), r, 2)
        name = 'Range' if btn['type'] == 'range' else ('Fire Rate' if btn['type'] == 'firerate' else 'Bullet')
        text = engine.font.render(f"{name} (Cost {btn['cost']})", True, (240, 240, 240))
        engine.screen.blit(text, (r.x + 10, r.y + 8))
        cur_t = None
        if engine.towers:
            if engine.selected_tower_idx is not None and 0 <= engine.selected_tower_idx < len(engine.towers):
                cur_t = engine.towers[engine.selected_tower_idx]
            else:
                cur_t = engine.towers[0]
        second_line = None
        if btn['type'] == 'range' and cur_t:
            old = int(cur_t.get('range', 120))
            new = old + engine.RANGE_UP_AMOUNT if hasattr(engine, 'RANGE_UP_AMOUNT') else old + 20
            second_line = f"Range: {old} → {new}"
        elif btn['type'] == 'firerate' and cur_t:
            old = int(cur_t.get('fire_rate', 500))
            delta = engine.FIRERATE_DELTA if hasattr(engine, 'FIRERATE_DELTA') else 50
            new = max(100, old - delta)
            second_line = f"Fire Rate: {old}ms → {new}ms"
        elif btn['type'] == 'bullet':
            bs_old = int(engine.bullet_speed)
            bs_new = bs_old + (engine.BULLET_SPEED_DELTA if hasattr(engine, 'BULLET_SPEED_DELTA') else 30)
            dmg_old = int(engine.bullet_damage)
            dmg_new = dmg_old + (engine.BULLET_DAMAGE_DELTA if hasattr(engine, 'BULLET_DAMAGE_DELTA') else 1)
            second_line = f"Bullet: spd {bs_old}→{bs_new}, dmg {dmg_old}→{dmg_new}"
        if second_line:
            stext = engine.font_small.render(second_line, True, (200, 200, 200))
            engine.screen.blit(stext, (r.x + 10, r.y + 26))

def handle_upgrade_click(engine, pos):
    if getattr(engine, 'upgrade_close_rect', None) and engine.upgrade_close_rect.collidepoint(pos):
        engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': 'upgrade:close'}))
        engine.upgrade_open = False
        return
    for btn in engine.get_upgrade_buttons():
        if btn['rect'].collidepoint(pos):
            engine.ev_manager.post(Event(EVENT_UI_CLICK, data={'id': f"upgrade:{btn['type']}"}))
            if engine.coins >= btn['cost']:
                engine.ev_manager.post(Event(EVENT_UPGRADE_TOWER, data={'type': btn['type'], 'cost': btn['cost']}))
            break
