from __future__ import annotations
from typing import Dict, Tuple, Optional, Any
import pygame
from core.config import TOWER_DEFINITIONS
from graphics import palette as pal
from graphics.ui_kit import draw_pixel_panel, draw_text_shadow
from gameplay.path import BuildSlot


BUILD_ORDER = ["archer", "artillery", "frost", "lightning"]
NODE_OFFSETS = [
    (-68, -54),  # Top-Left: Archer
    (68, -54),   # Top-Right: Artillery
    (-68, 54),   # Bottom-Left: Frost
    (68, 54),    # Bottom-Right: Lightning
]


class RadialMenu:
    """Kingdom Rush style tactical radial menu for building, upgrading, retargeting, and selling towers."""

    def __init__(self) -> None:
        self.active_slot: Optional[BuildSlot] = None
        self.node_rects: Dict[str, pygame.Rect] = {}
        self.hovered_key: Optional[str] = None
        self.anim_p: float = 0.0

    @property
    def is_open(self) -> bool:
        return self.active_slot is not None

    def open_for_slot(self, slot: BuildSlot) -> None:
        self.active_slot = slot
        self.anim_p = 0.0
        self.hovered_key = None
        self.node_rects.clear()

    def close(self) -> None:
        self.active_slot = None
        self.node_rects.clear()
        self.hovered_key = None

    def update(self, dt_ms: float, mouse_pos: Tuple[int, int]) -> None:
        if not self.is_open:
            return
        self.anim_p = min(1.0, self.anim_p + dt_ms / 160.0)
        self.hovered_key = None
        for k, r in self.node_rects.items():
            if r.collidepoint(mouse_pos):
                self.hovered_key = k
                break

    def draw(self, surface: pygame.Surface, game_scene: Any) -> None:
        if not self.is_open or self.active_slot is None:
            return

        slot = self.active_slot
        s = game_scene.ui_scale
        cx, cy = slot.pos
        cx = max(int(120 * s), min(game_scene.width - int(120 * s), cx))
        cy = max(int(110 * s), min(game_scene.height - int(125 * s), cy))

        ease = 1.0 - (1.0 - self.anim_p) ** 3
        ring_r = int(76 * s * ease)

        # 1. Draw Range Preview Circle
        if slot.tower is None:
            if self.hovered_key in TOWER_DEFINITIONS:
                rng_px = int(TOWER_DEFINITIONS[self.hovered_key]["levels"][0]["range"] * s)
                col = TOWER_DEFINITIONS[self.hovered_key]["color"]
                self._draw_range_circle(surface, slot.pos, rng_px, col)
        else:
            tw = slot.tower
            rng_px = int(tw.range * s)
            self._draw_range_circle(surface, slot.pos, rng_px, pal.UI_CYAN)
            if self.hovered_key == "upgrade" and tw.can_upgrade():
                nxt_rng = int(TOWER_DEFINITIONS[tw.tower_type]["levels"][tw.level]["range"] * s)
                self._draw_range_circle(surface, slot.pos, nxt_rng, pal.GOLD_SHINE)

        # 2. Connecting gold ring around slot
        if ring_r > 8:
            pygame.draw.circle(surface, pal.OUTLINE_DARK, (cx, cy), ring_r + 2, 4)
            pygame.draw.circle(surface, pal.UI_BORDER_GOLD, (cx, cy), ring_r, 2)

        self.node_rects.clear()
        node_w = int(64 * s)
        node_h = int(52 * s)

        if slot.tower is None:
            # --- EMPTY SLOT: 4 TOWER BUILD OPTIONS ---
            for idx, t_key in enumerate(BUILD_ORDER):
                cfg = TOWER_DEFINITIONS[t_key]
                lvl1 = cfg["levels"][0]
                cost = int(lvl1["cost"])
                can_afford = game_scene.coins >= cost
                ox, oy = NODE_OFFSETS[idx]
                nx = cx + int(ox * s * ease)
                ny = cy + int(oy * s * ease)
                r = pygame.Rect(0, 0, node_w, node_h)
                r.center = (nx, ny)
                self.node_rects[t_key] = r

                is_hov = self.hovered_key == t_key
                bg = (52, 46, 68) if can_afford else (34, 30, 42)
                if is_hov and can_afford:
                    bg = (74, 66, 96)
                border = pal.GOLD_SHINE if is_hov else (cfg["color"] if can_afford else pal.STONE_DARK)
                draw_pixel_panel(surface, r, bg_color=bg, border_color=border, gold_corners=False)

                turret_srf = game_scene.pixel_gen.get_tower_turret(t_key, 1, 0.0, 0)
                tw_s = pygame.transform.scale(turret_srf, (int(28 * s), int(28 * s)))
                surface.blit(tw_s, tw_s.get_rect(center=(r.centerx, r.top + int(16 * s))))

                cost_col = pal.GOLD_SHINE if can_afford else pal.UI_RED
                draw_text_shadow(
                    surface,
                    game_scene.font_small,
                    f"{cost}G",
                    cost_col,
                    pos=(r.centerx, r.bottom - int(10 * s)),
                )
                draw_text_shadow(
                    surface,
                    game_scene.font_small,
                    f"[{idx + 1}]",
                    pal.UI_TEXT_MUTED,
                    pos=(r.left + int(12 * s), r.top + int(10 * s)),
                )

            # Tooltip box if hovering a tower option
            if self.hovered_key in TOWER_DEFINITIONS:
                cfg = TOWER_DEFINITIONS[self.hovered_key]
                l1 = cfg["levels"][0]
                line1 = f"{cfg['name']} ({l1['cost']} Gold)"
                line2 = f"Damage: {l1['damage']}  |  Range: {l1['range']}  |  Rate: {1000.0/l1['fire_rate_ms']:.1f}/s"
                line3 = cfg["desc"]
                w1 = game_scene.font_mid.size(line1)[0]
                w2 = game_scene.font_small.size(line2)[0]
                w3 = game_scene.font_small.size(line3)[0]
                box_w = max(int(340 * s), w1 + int(32 * s), w2 + int(32 * s), w3 + int(32 * s))
                tip_r = pygame.Rect(0, 0, box_w, int(78 * s))
                tip_r.centerx = cx
                tip_r.top = cy + int(88 * s) if cy < game_scene.height * 0.62 else cy - int(168 * s)
                tip_r.clamp_ip(pygame.Rect(12, 62, game_scene.width - 24, game_scene.height - 135))
                draw_pixel_panel(surface, tip_r, bg_color=pal.UI_BG_DARK, border_color=cfg["color"])
                draw_text_shadow(
                    surface,
                    game_scene.font_mid,
                    line1,
                    cfg["color"],
                    pos=(tip_r.centerx, tip_r.top + int(18 * s)),
                )
                draw_text_shadow(
                    surface,
                    game_scene.font_small,
                    line2,
                    pal.GOLD_SHINE,
                    pos=(tip_r.centerx, tip_r.top + int(41 * s)),
                )
                draw_text_shadow(
                    surface,
                    game_scene.font_small,
                    line3,
                    pal.UI_TEXT_WHITE,
                    pos=(tip_r.centerx, tip_r.bottom - int(15 * s)),
                )

        else:
            # --- EXISTING TOWER: UPGRADE, TARGETING STRATEGY, SELL ---
            tw = slot.tower
            # Top node: Upgrade
            up_r = pygame.Rect(0, 0, int(118 * s), int(54 * s))
            up_r.center = (cx, cy - int(74 * s * ease))
            self.node_rects["upgrade"] = up_r

            if tw.can_upgrade():
                up_cost = tw.next_upgrade_cost()
                can_afford = game_scene.coins >= up_cost
                is_hov = self.hovered_key == "upgrade"
                border = pal.GOLD_SHINE if is_hov else (pal.UI_GREEN if can_afford else pal.STONE_DARK)
                draw_pixel_panel(surface, up_r, bg_color=pal.UI_BG_MID, border_color=border, gold_corners=False)
                up_icon = game_scene.pixel_gen.get_icon("upgrade")
                surface.blit(up_icon, up_icon.get_rect(center=(up_r.centerx, up_r.top + int(16 * s))))
                draw_text_shadow(
                    surface,
                    game_scene.font_small,
                    f"Lv.{tw.level + 1}: {up_cost}G [U]",
                    pal.GOLD_SHINE if can_afford else pal.UI_RED,
                    pos=(up_r.centerx, up_r.bottom - int(11 * s)),
                )
            else:
                draw_pixel_panel(surface, up_r, bg_color=pal.UI_BG_DARK, border_color=pal.GOLD_MID, gold_corners=False)
                draw_text_shadow(
                    surface,
                    game_scene.font_small,
                    "MAX LEVEL",
                    pal.GOLD_SHINE,
                    rect=up_r,
                )

            # Bottom-Left node: Cycle Strategy
            st_r = pygame.Rect(0, 0, int(102 * s), int(48 * s))
            st_r.center = (cx - int(82 * s * ease), cy + int(52 * s * ease))
            self.node_rects["strategy"] = st_r
            is_hov_st = self.hovered_key == "strategy"
            draw_pixel_panel(
                surface,
                st_r,
                bg_color=pal.UI_BG_MID,
                border_color=pal.UI_CYAN if is_hov_st else pal.STONE_LIGHT,
                gold_corners=False,
            )
            draw_text_shadow(
                surface,
                game_scene.font_small,
                "Target [T]:",
                pal.UI_TEXT_MUTED,
                pos=(st_r.centerx, st_r.top + int(14 * s)),
            )
            draw_text_shadow(
                surface,
                game_scene.font_small,
                tw.strategy.short_label,
                pal.UI_CYAN,
                pos=(st_r.centerx, st_r.bottom - int(13 * s)),
            )

            # Bottom-Right node: Sell Tower
            sl_r = pygame.Rect(0, 0, int(88 * s), int(48 * s))
            sl_r.center = (cx + int(82 * s * ease), cy + int(52 * s * ease))
            self.node_rects["sell"] = sl_r
            is_hov_sl = self.hovered_key == "sell"
            sell_val = tw.get_sell_value()
            draw_pixel_panel(
                surface,
                sl_r,
                bg_color=pal.UI_BG_MID,
                border_color=pal.UI_RED if is_hov_sl else pal.GOLD_DARK,
                gold_corners=False,
            )
            draw_text_shadow(
                surface,
                game_scene.font_small,
                "Sell [S]",
                pal.UI_RED,
                pos=(sl_r.centerx, sl_r.top + int(14 * s)),
            )
            draw_text_shadow(
                surface,
                game_scene.font_small,
                f"+{sell_val}G",
                pal.GOLD_SHINE,
                pos=(sl_r.centerx, sl_r.bottom - int(13 * s)),
            )

            # Info banner showing current stats
            info_txt = f"{tw.name} Lv.{tw.level} | Dmg: {int(tw.damage)} | Rate: {1000.0/tw.fire_rate_ms:.1f}/s"
            info_w = max(int(310 * s), game_scene.font_small.size(info_txt)[0] + int(28 * s))
            info_r = pygame.Rect(0, 0, info_w, int(40 * s))
            info_r.centerx = cx
            info_r.top = cy + int(88 * s) if cy < game_scene.height * 0.68 else cy - int(132 * s)
            info_r.clamp_ip(pygame.Rect(12, 62, game_scene.width - 24, game_scene.height - 135))
            draw_pixel_panel(surface, info_r, bg_color=pal.UI_BG_DARK, border_color=pal.UI_BORDER_GOLD, gold_corners=False)
            draw_text_shadow(
                surface,
                game_scene.font_small,
                info_txt,
                pal.UI_TEXT_WHITE,
                rect=info_r,
            )

    @staticmethod
    def _draw_range_circle(
        surface: pygame.Surface,
        center: Tuple[int, int],
        radius: int,
        color: Tuple[int, int, int],
    ) -> None:
        if radius <= 4:
            return
        srf = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
        c = (radius + 2, radius + 2)
        pygame.draw.circle(srf, (*color, 32), c, radius)
        pygame.draw.circle(srf, (*color, 185), c, radius, 2)
        surface.blit(srf, (center[0] - radius - 2, center[1] - radius - 2))
