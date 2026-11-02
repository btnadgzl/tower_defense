import pygame
from core.events import Event, EVENT_STATE_CHANGED
from ui.overlays import draw_paused_background_to, draw_paused_controls_to

def start_transition(engine, next_state, style='slide', dir=None):
    if next_state == engine.state:
        return
    engine.transition_active = True
    engine.transition_ms = 0
    engine.transition_from = engine.state
    engine.transition_to = next_state
    engine.transition_style = style or 'slide'
    if dir is not None:
        engine.transition_dir = 1 if dir >= 0 else -1
    else:
        if engine.transition_style == 'slide':
            if engine.transition_from == 'menu' and engine.transition_to == 'settings':
                engine.transition_dir = 1
            elif engine.transition_from == 'settings' and engine.transition_to == 'menu':
                engine.transition_dir = -1
            else:
                engine.transition_dir = 1

def render_scene_for_state(engine, state, surface):
    old_state = engine.state
    old_scr = engine.screen
    engine.state = state
    engine.screen = surface
    engine.draw_background()
    engine.draw_towers()
    engine.draw_enemies()
    engine.draw_bullets()
    engine.draw_rain()
    engine.draw_ui()
    engine.draw_overlays()
    engine.screen = old_scr
    engine.state = old_state

def render_with_transition(engine):
    dt_ms = engine.clock.get_time()
    engine.transition_ms = min(engine.transition_dur, engine.transition_ms + dt_ms)
    p = engine.transition_ms / float(engine.transition_dur)
    p_e = p * p * (3 - 2 * p)
    from_surf = pygame.Surface((engine.width, engine.height), pygame.SRCALPHA)
    to_surf = pygame.Surface((engine.width, engine.height), pygame.SRCALPHA)
    render_scene_for_state(engine, engine.transition_from or engine.state, from_surf)
    render_scene_for_state(engine, engine.transition_to or engine.state, to_surf)
    if getattr(engine, 'transition_style', 'slide') == 'slide':
        old_x = int(-getattr(engine, 'transition_dir', 1) * engine.width * p_e)
        new_x = int(getattr(engine, 'transition_dir', 1) * engine.width * (1.0 - p_e))
        engine.screen.blit(from_surf, (old_x, 0))
        engine.screen.blit(to_surf, (new_x, 0))
    else:
        if engine.transition_from == 'playing' and engine.transition_to == 'paused':
            engine.screen.blit(from_surf, (0, 0))
            draw_paused_background_to(engine, engine.screen)
            ctrl = pygame.Surface((engine.width, engine.height), pygame.SRCALPHA)
            draw_paused_controls_to(engine, ctrl)
            z = 0.85 + 0.15 * p_e
            tw = max(1, int(engine.width * z)); th = max(1, int(engine.height * z))
            scaled = pygame.transform.smoothscale(ctrl, (tw, th))
            engine.screen.blit(scaled, scaled.get_rect(center=(engine.width//2, engine.height//2)))
        elif engine.transition_from == 'paused' and engine.transition_to == 'playing':
            engine.screen.blit(to_surf, (0, 0))
            alpha = max(0, min(160, int(160 * (1.0 - p_e))))
            overlay = pygame.Surface((engine.width, engine.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha))
            engine.screen.blit(overlay, (0, 0))
            ctrl = pygame.Surface((engine.width, engine.height), pygame.SRCALPHA)
            draw_paused_controls_to(engine, ctrl)
            z = 1.15 - 0.15 * p_e
            tw = max(1, int(engine.width * z)); th = max(1, int(engine.height * z))
            scaled = pygame.transform.smoothscale(ctrl, (tw, th))
            engine.screen.blit(scaled, scaled.get_rect(center=(engine.width//2, engine.height//2)))
        else:
            engine.screen.blit(to_surf, (0, 0))
    if engine.transition_ms >= engine.transition_dur:
        engine.transition_active = False
        engine.state = engine.transition_to or engine.state
        try:
            engine.ev_manager.post(Event(EVENT_STATE_CHANGED, data={'state': engine.state}))
        except Exception:
            pass
