from __future__ import annotations
from typing import Tuple, Optional
import pygame
from graphics import palette as pal


def draw_text_shadow(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    color: Tuple[int, int, int] = pal.UI_TEXT_WHITE,
    pos: Optional[Tuple[int, int]] = None,
    rect: Optional[pygame.Rect] = None,
    align: str = "center",
    shadow_color: Tuple[int, int, int] = (14, 10, 22),
) -> pygame.Rect:
    txt_surf = font.render(text, True, color)
    shd_surf = font.render(text, True, shadow_color)
    if rect is not None:
        r = txt_surf.get_rect()
        setattr(r, align, getattr(rect, align))
    elif pos is not None:
        r = txt_surf.get_rect(**{align: pos})
    else:
        r = txt_surf.get_rect()
    surface.blit(shd_surf, (r.x + 2, r.y + 2))
    surface.blit(shd_surf, (r.x + 1, r.y + 1))
    surface.blit(txt_surf, r)
    return r


def draw_pixel_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    bg_color: Tuple[int, int, int] = pal.UI_BG_DARK,
    border_color: Tuple[int, int, int] = pal.UI_BORDER_GOLD,
    gold_corners: bool = True,
    alpha: int = 238,
) -> None:
    """Draws a medieval pixel-art framed panel with beveled inner border and corner studs."""
    # Drop shadow
    sh = pygame.Surface((rect.width + 6, rect.height + 6), pygame.SRCALPHA)
    pygame.draw.rect(sh, (8, 6, 14, 130), (4, 4, rect.width, rect.height), border_radius=4)
    surface.blit(sh, (rect.x, rect.y))

    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill((*bg_color, alpha))
    surface.blit(panel, rect.topleft)

    # Outer dark pixel contour
    pygame.draw.rect(surface, pal.OUTLINE_DARK, rect.inflate(2, 2), 2)
    # Main metallic/gold border
    pygame.draw.rect(surface, border_color, rect, 2)
    # Inner highlight bevel
    inner = rect.inflate(-6, -6)
    if inner.width > 4 and inner.height > 4:
        pygame.draw.rect(surface, pal.UI_BG_LIGHT, inner, 1)

    if gold_corners and rect.width >= 24 and rect.height >= 24:
        stud_sz = 5
        corners = [
            (rect.left + 2, rect.top + 2),
            (rect.right - 2 - stud_sz, rect.top + 2),
            (rect.left + 2, rect.bottom - 2 - stud_sz),
            (rect.right - 2 - stud_sz, rect.bottom - 2 - stud_sz),
        ]
        for cx, cy in corners:
            pygame.draw.rect(surface, pal.GOLD_LIGHT, (cx, cy, stud_sz, stud_sz))
            pygame.draw.rect(surface, pal.OUTLINE_DARK, (cx, cy, stud_sz, stud_sz), 1)


def draw_pixel_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font: pygame.font.Font,
    hovered: bool = False,
    active: bool = False,
    disabled: bool = False,
    accent_color: Optional[Tuple[int, int, int]] = None,
    icon: Optional[pygame.Surface] = None,
) -> None:
    """Draws a responsive pixel-art button with bevels, hover highlight, and optional icon."""
    draw_r = rect.move(0, 1 if active else 0)

    # Shadow
    pygame.draw.rect(surface, (10, 8, 16), draw_r.move(0, 3))

    if disabled:
        bg = (42, 40, 50)
        border = pal.STONE_DARK
        txt_col = pal.UI_TEXT_MUTED
    elif active:
        bg = accent_color or pal.GOLD_MID
        border = pal.GOLD_SHINE
        txt_col = pal.UI_TEXT_WHITE
    elif hovered:
        base = accent_color or pal.UI_BG_LIGHT
        bg = (min(255, base[0] + 28), min(255, base[1] + 28), min(255, base[2] + 28))
        border = pal.GOLD_SHINE
        txt_col = pal.GOLD_SHINE
    else:
        bg = accent_color or pal.UI_BG_MID
        border = pal.UI_BORDER_GOLD
        txt_col = pal.UI_TEXT_WHITE

    pygame.draw.rect(surface, bg, draw_r)
    # Top highlight strip
    if not disabled:
        hi = (min(255, bg[0] + 35), min(255, bg[1] + 35), min(255, bg[2] + 35))
        pygame.draw.line(surface, hi, (draw_r.left + 2, draw_r.top + 2), (draw_r.right - 3, draw_r.top + 2), 2)
    pygame.draw.rect(surface, pal.OUTLINE_DARK, draw_r.inflate(2, 2), 2)
    pygame.draw.rect(surface, border, draw_r, 2)

    if icon is not None:
        iw, ih = icon.get_size()
        txt_srf = font.render(text, True, txt_col)
        total_w = iw + 8 + txt_srf.get_width()
        sx = draw_r.centerx - total_w // 2
        surface.blit(icon, (sx, draw_r.centery - ih // 2))
        draw_text_shadow(
            surface,
            font,
            text,
            txt_col,
            pos=(sx + iw + 8, draw_r.centery),
            align="midleft",
        )
    else:
        draw_text_shadow(surface, font, text, txt_col, rect=draw_r, align="center")


def draw_pixel_bar(
    surface: pygame.Surface,
    rect: pygame.Rect,
    ratio: float,
    fill_color: Tuple[int, int, int],
    bg_color: Tuple[int, int, int] = (20, 18, 28),
    border_color: Tuple[int, int, int] = pal.STONE_MID,
    label: Optional[str] = None,
    font: Optional[pygame.font.Font] = None,
) -> None:
    clamped = max(0.0, min(1.0, float(ratio)))
    pygame.draw.rect(surface, bg_color, rect)
    fill_w = int((rect.width - 4) * clamped)
    if fill_w > 0:
        f_rect = pygame.Rect(rect.left + 2, rect.top + 2, fill_w, rect.height - 4)
        pygame.draw.rect(surface, fill_color, f_rect)
        hi_col = (min(255, fill_color[0] + 45), min(255, fill_color[1] + 45), min(255, fill_color[2] + 45))
        if f_rect.height >= 6:
            pygame.draw.line(surface, hi_col, (f_rect.left, f_rect.top + 1), (f_rect.right - 1, f_rect.top + 1), 2)
    pygame.draw.rect(surface, pal.OUTLINE_DARK, rect.inflate(2, 2), 2)
    pygame.draw.rect(surface, border_color, rect, 2)
    if label and font:
        draw_text_shadow(surface, font, label, pal.UI_TEXT_WHITE, rect=rect, align="center")

