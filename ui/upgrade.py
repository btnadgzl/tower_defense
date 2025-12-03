import pygame
from typing import Any
from core.events import Event, EVENT_UPGRADE_TOWER, EVENT_UI_CLICK

def _ease_out_cubic(p):
    q = 1.0 - p
    return 1.0 - q*q*q

def draw_upgrade_panel(engine: Any) -> None:
    s = getattr(engine, 'ui_scale', 1.0)
    types = ['sword','range','bullet_power','bullet_speed']
    desired_open = bool(engine.upgrade_open)
    if not hasattr(engine, 'upgrade_anim_p'):
        engine.upgrade_anim_p = 1.0 if desired_open else 0.0
        engine.upgrade_anim_start_x = engine.width
        engine.upgrade_anim_end_x = engine.width - int(0.90 * engine.width)
    if getattr(engine, 'upgrade_anim_target_open', None) != desired_open:
        engine.upgrade_anim_target_open = desired_open
        engine.upgrade_anim_p = 0.0
        engine.upgrade_anim_start_x = getattr(engine, 'upgrade_anim_current_x', engine.width)
        engine.upgrade_anim_end_x = engine.width - int(0.90 * engine.width) if desired_open else engine.width
    dur = 0.35
    dt = getattr(engine, 'last_dt_ms', 16) / 1000.0
    if engine.upgrade_anim_p < 1.0:
        engine.upgrade_anim_p = min(1.0, engine.upgrade_anim_p + dt / dur)
    e = _ease_out_cubic(engine.upgrade_anim_p)
    cur_x = int(engine.upgrade_anim_start_x + (engine.upgrade_anim_end_x - engine.upgrade_anim_start_x) * e)
    engine.upgrade_anim_current_x = cur_x
    engine.upgrade_anim_running = engine.upgrade_anim_p < 1.0
    
    # Panel background
    panel_h = int(0.45 * engine.height)
    panel_w = int(0.92 * engine.width)
    rect = pygame.Rect(cur_x, int(0.10 * engine.height), panel_w, panel_h)
    if getattr(engine, 'upgrademenu_img', None):
        bg = pygame.transform.smoothscale(engine.upgrademenu_img, (rect.width, rect.height))
        engine.screen.blit(bg, rect)
        bg_w, bg_h = engine.upgrademenu_img.get_size()
    else:
        pygame.draw.rect(engine.screen, (30,30,30), rect); pygame.draw.rect(engine.screen, (80,80,80), rect, 2)
        bg_w, bg_h = rect.width, rect.height
    
    card_centers_pct = getattr(engine, 'upgrade_card_centers_pct', [0.238, 0.492, 0.747, 0.875])
    card_center_y_pct = getattr(engine, 'upgrade_card_center_y_pct', 0.445)
    card_w_pct = getattr(engine, 'upgrade_card_w_pct', 0.19)
    card_h_pct = getattr(engine, 'upgrade_card_h_pct', 0.58)
    container_w_ratio = getattr(engine, 'upgrade_container_w_ratio', 0.50)
    slot_gap_ratio = getattr(engine, 'upgrade_slot_gap_ratio', 0.006)
    bar_y_ratio = getattr(engine, 'upgrade_bar_y_ratio', 0.11)
    plus_px = getattr(engine, 'upgrade_plus_px', {
        'sword': (308, 392, 56, 56),
        'range': (617, 392, 56, 56),
        'bullet_power': (926, 392, 56, 56),
        'bullet_speed': (1235, 392, 56, 56),
    })
    
    engine.upgrade_plus_rects = {}
    for i,typ in enumerate(types):
        cw = int(card_w_pct * rect.width)
        ch = int(card_h_pct * rect.height)
        offx = getattr(engine, 'upgrade_card_center_x_offsets_pct', {}).get(typ, 0.0)
        offy = getattr(engine, 'upgrade_card_center_y_offsets_pct', {}).get(typ, 0.0)
        cx = rect.x + int((card_centers_pct[i] + offx) * rect.width)
        cy = rect.y + int((card_center_y_pct + offy) * rect.height)
        card = pygame.Rect(0, 0, cw, ch)
        card.center = (cx, cy)
        
        # Progress fill over PNG bar slots (no frame drawing)
        lvl = engine.upgrade_levels.get(typ, 0)
        limit = engine.upgrade_limits.get(typ, 5)
        cwr_map = getattr(engine, 'upgrade_container_w_ratio_by_type', {})
        byr_map = getattr(engine, 'upgrade_bar_y_ratio_by_type', {})
        container_w = int(cwr_map.get(typ, container_w_ratio) * cw)
        slot_gap = max(2, int(slot_gap_ratio * rect.width))
        slot_w = max(12, int((container_w - (limit - 1) * slot_gap) / max(1, limit)))
        start_x = card.centerx - container_w // 2
        slot_h = max(6, int(slot_w * 0.5))
        slot_y = card.bottom - int(byr_map.get(typ, bar_y_ratio) * ch)
        for k in range(lvl):
            bx = start_x + k * (slot_w + slot_gap)
            if getattr(engine, 'upgrade_level_img', None):
                base = engine.upgrade_level_img
                img = pygame.transform.smoothscale(base, (slot_w, slot_h)) if base.get_size() != (slot_w, slot_h) else base
                engine.screen.blit(img, (bx, slot_y))
            else:
                fill = pygame.Surface((slot_w, slot_h), pygame.SRCALPHA)
                fill.fill((50, 255, 50, 160))
                engine.screen.blit(fill, (bx, slot_y))
        
        # '+' hitbox from PNG pixel anchors, scaled to panel rect
        px, py, pw, ph = plus_px[typ]
        pr = pygame.Rect(
            rect.x + int((px / float(bg_w)) * rect.width),
            rect.y + int((py / float(bg_h)) * rect.height),
            int((pw / float(bg_w)) * rect.width),
            int((ph / float(bg_h)) * rect.height),
        )
        pofs = getattr(engine, 'upgrade_plus_offsets_pct_by_type', {}).get(typ, (0.0, 0.0))
        pr.x += int(pofs[0] * rect.width)
        pr.y += int(pofs[1] * rect.height)
        engine.upgrade_plus_rects[typ] = pr
        if getattr(engine, 'upgrade_debug', False):
            pygame.draw.rect(engine.screen, (0, 200, 255), card, 1)
            pygame.draw.rect(engine.screen, (0, 180, 0), (start_x, slot_y, container_w, slot_h), 1)
            pygame.draw.rect(engine.screen, (255, 120, 0), pr, 2)

def handle_upgrade_click(engine: Any, pos) -> None:
    types = ['sword','range','bullet_power','bullet_speed']
    for typ in types:
        r = getattr(engine, 'upgrade_plus_rects', {}).get(typ)
        if r and r.collidepoint(pos):
            lvl = engine.upgrade_levels.get(typ, 0)
            limit = engine.upgrade_limits.get(typ, 0)
            cost = engine.UPGRADE_COSTS.get(typ, 0)
            if lvl >= limit or engine.coins < cost:
                continue
            engine.ev_manager.post(Event(EVENT_UPGRADE_TOWER, data={'type': typ, 'cost': cost}))
            break
