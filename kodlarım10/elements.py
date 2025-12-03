from __future__ import annotations
import pygame
from typing import Callable, Optional, Tuple


class UIElement:
    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect

    def draw(self, surface: pygame.Surface) -> None:
        pass

    def collidepoint(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


class UIButton(UIElement):
    def __init__(self, rect: pygame.Rect, image: Optional[pygame.Surface] = None, label: Optional[str] = None, font: Optional[pygame.font.Font] = None) -> None:
        super().__init__(rect)
        self.image = image
        self.label = label
        self.font = font

    def draw(self, surface: pygame.Surface) -> None:
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, (220, 220, 220), self.rect)
            pygame.draw.rect(surface, (120, 120, 120), self.rect, 2)
            if self.label and self.font:
                ts = self.font.render(self.label, True, (20, 20, 20))
                surface.blit(ts, ts.get_rect(center=self.rect.center))


class UIPanel(UIElement):
    def __init__(self, rect: pygame.Rect, image: Optional[pygame.Surface] = None) -> None:
        super().__init__(rect)
        self.image = image

    def draw(self, surface: pygame.Surface) -> None:
        if self.image:
            img = pygame.transform.smoothscale(self.image, (self.rect.width, self.rect.height))
            surface.blit(img, self.rect)
        else:
            pygame.draw.rect(surface, (30, 30, 30), self.rect)
            pygame.draw.rect(surface, (80, 80, 80), self.rect, 2)


class UIText(UIElement):
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font, color: Tuple[int, int, int] = (240, 240, 240)) -> None:
        super().__init__(rect)
        self.text = text
        self.font = font
        self.color = color

    def draw(self, surface: pygame.Surface) -> None:
        ts = self.font.render(self.text, True, self.color)
        r = ts.get_rect(center=self.rect.center)
        surface.blit(ts, r)

