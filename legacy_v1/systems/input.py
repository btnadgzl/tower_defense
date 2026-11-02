import pygame
from typing import Any
from core.events import Event, EVENT_QUIT, EVENT_MANUAL_FIRE, EVENT_TOGGLE_UPGRADE_PANEL, EVENT_TOGGLE_PAUSE, EVENT_UPGRADE_TOWER, EVENT_MOUSE_CLICK, EVENT_ULTI_USED, EVENT_TOGGLE_UPGRADE_DEBUG, EVENT_UPGRADE_DEBUG_ADJUST, EVENT_UPGRADE_DEBUG_SAVE, EVENT_UPGRADE_DEBUG_SELECT_TYPE, EVENT_UPGRADE_DEBUG_TOGGLE_LIMITS, EVENT_TOGGLE_MENU_DEBUG, EVENT_TOGGLE_SETTINGS_DEBUG, EVENT_TOGGLE_GO_DEBUG, EVENT_TOGGLE_PAUSED_DEBUG, EVENT_TOGGLE_DEBUG_RESIZE_MODE, EVENT_TOGGLE_HUD_DEBUG

class KeyboardController:
    def __init__(self, ev_manager: Any) -> None:
        self.ev_manager = ev_manager
        self.ev_manager.register(self)

    def notify(self, event: Event) -> None:
        pass

    def check_inputs(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.ev_manager.post(Event(EVENT_QUIT))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.ev_manager.post(Event(EVENT_MANUAL_FIRE))
                elif event.key == pygame.K_u:
                    self.ev_manager.post(Event(EVENT_TOGGLE_UPGRADE_PANEL))
                elif event.key == pygame.K_q:
                    self.ev_manager.post(Event(EVENT_ULTI_USED))
                elif event.key == pygame.K_F1:
                    self.ev_manager.post(Event(EVENT_TOGGLE_UPGRADE_DEBUG))
                elif event.key == pygame.K_F5:
                    self.ev_manager.post(Event(EVENT_TOGGLE_MENU_DEBUG))
                elif event.key == pygame.K_F6:
                    self.ev_manager.post(Event(EVENT_TOGGLE_SETTINGS_DEBUG))
                elif event.key == pygame.K_F7:
                    self.ev_manager.post(Event(EVENT_TOGGLE_GO_DEBUG))
                elif event.key == pygame.K_F8:
                    self.ev_manager.post(Event(EVENT_TOGGLE_PAUSED_DEBUG))
                elif event.key == pygame.K_F9:
                    self.ev_manager.post(Event(EVENT_TOGGLE_DEBUG_RESIZE_MODE))
                elif event.key == pygame.K_F10:
                    self.ev_manager.post(Event(EVENT_TOGGLE_HUD_DEBUG))
                elif event.key == pygame.K_F4:
                    self.ev_manager.post(Event(EVENT_UPGRADE_DEBUG_TOGGLE_LIMITS))
                elif event.key == pygame.K_TAB:
                    self.ev_manager.post(Event(EVENT_UPGRADE_DEBUG_ADJUST, data={'field': 'cycle'}))
                elif event.key == pygame.K_F2:
                    self.ev_manager.post(Event(EVENT_UPGRADE_DEBUG_SELECT_TYPE, data={'dir': 'next'}))
                elif event.key == pygame.K_F3:
                    self.ev_manager.post(Event(EVENT_UPGRADE_DEBUG_SELECT_TYPE, data={'dir': 'prev'}))
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    mods = pygame.key.get_mods()
                    base = 0.003
                    mult = 1.0
                    if mods & pygame.KMOD_SHIFT:
                        mult *= 3.0
                    if mods & pygame.KMOD_CTRL:
                        mult *= 6.0
                    if mods & pygame.KMOD_ALT:
                        mult *= 12.0
                    step = base * mult
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        axis = 'x'; delta = -step if event.key == pygame.K_LEFT else step
                    else:
                        axis = 'y'; delta = -step if event.key == pygame.K_UP else step
                    self.ev_manager.post(Event(EVENT_UPGRADE_DEBUG_ADJUST, data={'axis': axis, 'delta': delta}))
                elif event.key == pygame.K_s:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL:
                        self.ev_manager.post(Event(EVENT_UPGRADE_DEBUG_SAVE))
                elif event.key == pygame.K_ESCAPE:
                    self.ev_manager.post(Event(EVENT_TOGGLE_PAUSE))
                elif event.key == pygame.K_1:
                    self.ev_manager.post(Event(EVENT_UPGRADE_TOWER, data={'type': 'range', 'cost': 5}))
                elif event.key == pygame.K_2:
                    self.ev_manager.post(Event(EVENT_UPGRADE_TOWER, data={'type': 'firerate', 'cost': 5}))
                elif event.key == pygame.K_3:
                    self.ev_manager.post(Event(EVENT_UPGRADE_TOWER, data={'type': 'bullet', 'cost': 5}))
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                self.ev_manager.post(Event(EVENT_MOUSE_CLICK, data={'pos': pos}))
