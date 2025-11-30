import pygame
from core.events import Event, EVENT_QUIT, EVENT_MANUAL_FIRE, EVENT_TOGGLE_UPGRADE_PANEL, EVENT_TOGGLE_PAUSE, EVENT_UPGRADE_TOWER, EVENT_MOUSE_CLICK

class KeyboardController:
    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.register(self)

    def notify(self, event):
        pass

    def check_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.ev_manager.post(Event(EVENT_QUIT))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.ev_manager.post(Event(EVENT_MANUAL_FIRE))
                elif event.key == pygame.K_u:
                    self.ev_manager.post(Event(EVENT_TOGGLE_UPGRADE_PANEL))
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
