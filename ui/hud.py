from __future__ import annotations
from typing import Any, Tuple
import pygame
from core.config import SPELLS_CONFIG, HERO_CONFIG
from graphics import palette as pal
from graphics.ui_kit import draw_pixel_panel, draw_pixel_button, draw_pixel_bar, draw_text_shadow


class GameHUD:
    """Renders the top kingdom status bar, wave controls, active spell buttons, Hero command bar, and Boss HP bar."""

    def __init__(self) -> None:
        self.call_wave_rect = pygame.Rect(0, 0, 10, 10)
        self.light_btn_rect = pygame.Rect(0, 0, 10, 10)
        self.speed_btn_rect = pygame.Rect(0, 0, 10, 10)
        self.pause_btn_rect = pygame.Rect(0, 0, 10, 10)
        self.meteor_btn_rect = pygame.Rect(0, 0, 10, 10)
        self.blizzard_btn_rect = pygame.Rect(0, 0, 10, 10)
        self.hero_skill_btn_rect = pygame.Rect(0, 0, 10, 10)
        self.hero_status_rect = pygame.Rect(0, 0, 10, 10)

    def draw(self, surface: pygame.Surface, game_scene: Any) -> None:
        s = game_scene.ui_scale
        w, h = game_scene.width, game_scene.height
        mx, my = pygame.mouse.get_pos()

        # 1. Top Left Panel: Castle HP & Gold & Score
        status_rect = pygame.Rect(int(12 * s), int(10 * s), int(350 * s), int(46 * s))
        draw_pixel_panel(surface, status_rect, bg_color=pal.UI_BG_DARK, border_color=pal.UI_BORDER_GOLD)

        heart_ic = game_scene.pixel_gen.get_icon("heart")
        surface.blit(heart_ic, (status_rect.left + int(12 * s), status_rect.centery - heart_ic.get_height() // 2))
        hp_bar_r = pygame.Rect(
            status_rect.left + int(42 * s),
            status_rect.centery - int(11 * s),
            int(115 * s),
            int(22 * s),
        )
        hp_ratio = game_scene.castle_hp / max(1.0, float(game_scene.castle_hp_max))
        hp_col = pal.UI_GREEN if hp_ratio > 0.5 else (pal.GOLD_MID if hp_ratio > 0.25 else pal.UI_RED)
        draw_pixel_bar(
            surface,
            hp_bar_r,
            hp_ratio,
            fill_color=hp_col,
            label=f"{int(game_scene.castle_hp)}/{int(game_scene.castle_hp_max)}",
            font=game_scene.font_small,
        )

        coin_ic = game_scene.pixel_gen.get_icon("coin")
        coin_x = hp_bar_r.right + int(16 * s)
        surface.blit(coin_ic, (coin_x, status_rect.centery - coin_ic.get_height() // 2))
        draw_text_shadow(
            surface,
            game_scene.font_mid,
            f"{game_scene.coins}",
            pal.GOLD_SHINE,
            pos=(coin_x + coin_ic.get_width() + int(6 * s), status_rect.centery),
            align="midleft",
        )

        draw_text_shadow(
            surface,
            game_scene.font_small,
            f"Score: {game_scene.score}",
            pal.UI_TEXT_MUTED,
            pos=(status_rect.right - int(14 * s), status_rect.centery),
            align="midright",
        )

        # 2. Top Center Panel: Wave Info & Early Wave Call Button
        wave_mgr = game_scene.wave_mgr
        wave_panel = pygame.Rect(0, int(10 * s), int(380 * s), int(46 * s))
        wave_panel.centerx = w // 2
        draw_pixel_panel(surface, wave_panel, bg_color=pal.UI_BG_DARK, border_color=pal.UI_BORDER_GOLD)

        wave_ic = game_scene.pixel_gen.get_icon("wave")
        surface.blit(wave_ic, (wave_panel.left + int(12 * s), wave_panel.centery - wave_ic.get_height() // 2))

        if wave_mgr.state == "prep":
            secs = max(0, int(wave_mgr.prep_timer_ms / 1000.0) + 1)
            nxt_num = wave_mgr.current_wave + 1
            draw_text_shadow(
                surface,
                game_scene.font_small,
                f"Next Wave {nxt_num} ({secs}s)",
                pal.UI_TEXT_WHITE,
                pos=(wave_panel.left + int(42 * s), wave_panel.centery),
                align="midleft",
            )
            self.call_wave_rect = pygame.Rect(
                wave_panel.right - int(162 * s),
                wave_panel.top + int(7 * s),
                int(152 * s),
                int(32 * s),
            )
            bonus = max(5, int(wave_mgr.prep_timer_ms / 400.0)) if wave_mgr.current_wave > 0 else 0
            btn_txt = f"Call (+{bonus}G) [N]" if bonus > 0 else "Start Wave [N]"
            draw_pixel_button(
                surface,
                self.call_wave_rect,
                btn_txt,
                game_scene.font_small,
                hovered=self.call_wave_rect.collidepoint(mx, my),
                accent_color=pal.ARCHER_GREEN_DARK,
            )
        else:
            self.call_wave_rect = pygame.Rect(0, 0, 0, 0)
            draw_text_shadow(
                surface,
                game_scene.font_mid,
                f"Wave {wave_mgr.current_wave}/{wave_mgr.max_campaign_waves}: {wave_mgr.wave_title}",
                pal.GOLD_SHINE,
                pos=(wave_panel.left + int(42 * s), wave_panel.centery),
                align="midleft",
            )

        # 3. Top Right Controls: Lighting Mode [L], Speed Toggle (1x/2x) & Pause
        self.light_btn_rect = pygame.Rect(w - int(350 * s), int(12 * s), int(146 * s), int(40 * s))
        self.speed_btn_rect = pygame.Rect(w - int(195 * s), int(12 * s), int(86 * s), int(40 * s))
        self.pause_btn_rect = pygame.Rect(w - int(100 * s), int(12 * s), int(88 * s), int(40 * s))

        light_label = f"Light: {game_scene.lighting.mode_label} [L]"
        draw_pixel_button(
            surface,
            self.light_btn_rect,
            light_label,
            game_scene.font_small,
            hovered=self.light_btn_rect.collidepoint(mx, my),
            active=(game_scene.lighting.mode != "day"),
            accent_color=pal.ARCANE_DARK if game_scene.lighting.darkness_factor > 0.25 else pal.UI_BG_MID,
        )

        spd_label = f"Speed: {int(game_scene.game_speed)}x"
        draw_pixel_button(
            surface,
            self.speed_btn_rect,
            spd_label,
            game_scene.font_small,
            hovered=self.speed_btn_rect.collidepoint(mx, my),
            active=(game_scene.game_speed > 1.0),
            accent_color=pal.ROYAL_BLUE_DARK if game_scene.game_speed > 1.0 else pal.UI_BG_MID,
        )
        draw_pixel_button(
            surface,
            self.pause_btn_rect,
            "Pause",
            game_scene.font_small,
            hovered=self.pause_btn_rect.collidepoint(mx, my),
        )

        # 4. Bottom Bar: Active Kingdom Spells ([Q] Meteor, [W] Blizzard) + Hero Skill ([E]) & Hero Status Card
        self.meteor_btn_rect = pygame.Rect(int(14 * s), h - int(66 * s), int(200 * s), int(52 * s))
        self.blizzard_btn_rect = pygame.Rect(int(222 * s), h - int(66 * s), int(204 * s), int(52 * s))
        self.hero_skill_btn_rect = pygame.Rect(int(434 * s), h - int(66 * s), int(210 * s), int(52 * s))
        self.hero_status_rect = pygame.Rect(int(652 * s), h - int(66 * s), int(306 * s), int(52 * s))

        self._draw_spell_button(
            surface,
            game_scene,
            self.meteor_btn_rect,
            "meteor",
            SPELLS_CONFIG["meteor"]["name"],
            "Q",
            game_scene.spell_cooldowns["meteor"],
            SPELLS_CONFIG["meteor"]["cooldown_ms"],
            pal.FIRE_MID,
            (mx, my),
        )
        self._draw_spell_button(
            surface,
            game_scene,
            self.blizzard_btn_rect,
            "blizzard",
            SPELLS_CONFIG["blizzard"]["name"],
            "W",
            game_scene.spell_cooldowns["blizzard"],
            SPELLS_CONFIG["blizzard"]["cooldown_ms"],
            pal.FROST_MID,
            (mx, my),
        )

        hero = getattr(game_scene, "hero", None)
        if hero is not None:
            self._draw_spell_button(
                surface,
                game_scene,
                self.hero_skill_btn_rect,
                "holy_strike",
                HERO_CONFIG["skill"]["name"],
                "E",
                hero.skill_cd_ms if hero.alive else hero.respawn_timer_ms,
                hero.skill_max_cd_ms if hero.alive else hero.respawn_max_ms,
                pal.GOLD_MID,
                (mx, my),
            )
            self._draw_hero_status_card(surface, game_scene, hero, self.hero_status_rect)

        # 5. Boss Health Bar (if a Boss Golem is alive)
        boss = next((e for e in game_scene.enemies if e.alive and e.boss), None)
        if boss is not None:
            b_rect = pygame.Rect(0, int(64 * s), int(420 * s), int(24 * s))
            b_rect.centerx = w // 2
            draw_pixel_bar(
                surface,
                b_rect,
                boss.hp / max(1.0, boss.hp_max),
                fill_color=pal.CRIMSON_LIGHT,
                border_color=pal.GOLD_MID,
                label=f"{boss.name}: {int(boss.hp)} / {int(boss.hp_max)}",
                font=game_scene.font_small,
            )

        # 6. FPS Counter (Bottom-Right) if enabled in settings
        if game_scene.settings.get("show_fps", True):
            fps = int(game_scene.clock.get_fps())
            draw_text_shadow(
                surface,
                game_scene.font_small,
                f"FPS: {fps}",
                pal.UI_TEXT_MUTED,
                pos=(w - int(14 * s), h - int(16 * s)),
                align="bottomright",
            )

    @staticmethod
    def _draw_hero_status_card(
        surface: pygame.Surface,
        game_scene: Any,
        hero: Any,
        rect: pygame.Rect,
    ) -> None:
        s = game_scene.ui_scale
        draw_pixel_panel(surface, rect, bg_color=pal.UI_BG_DARK, border_color=pal.GOLD_MID, gold_corners=False)

        # Mini Paladin sprite icon on left
        ic = game_scene.pixel_gen.get_icon("hero")
        surface.blit(ic, (rect.left + int(10 * s), rect.centery - ic.get_height() // 2))

        tx = rect.left + int(42 * s)
        lvl_txt = f"{hero.name} Lv.{hero.level}"
        draw_text_shadow(
            surface,
            game_scene.font_small,
            lvl_txt,
            pal.GOLD_SHINE,
            pos=(tx, rect.top + int(15 * s)),
            align="midleft",
        )
        draw_text_shadow(
            surface,
            game_scene.font_small,
            "[RMB/H: Move]",
            pal.UI_CYAN,
            pos=(rect.right - int(10 * s), rect.top + int(15 * s)),
            align="midright",
        )

        bar_r = pygame.Rect(tx, rect.bottom - int(19 * s), rect.width - int(52 * s), int(13 * s))
        if hero.alive:
            ratio = hero.hp / max(1.0, hero.hp_max)
            draw_pixel_bar(
                surface,
                bar_r,
                ratio,
                fill_color=pal.UI_GREEN if ratio > 0.4 else pal.GOLD_MID,
                label=f"HP {int(hero.hp)}/{int(hero.hp_max)} | XP {int(hero.xp_ratio * 100)}%",
                font=game_scene.font_small,
            )
        else:
            ratio = 1.0 - (hero.respawn_timer_ms / max(1.0, hero.respawn_max_ms))
            draw_pixel_bar(
                surface,
                bar_r,
                ratio,
                fill_color=pal.UI_RED,
                label=f"Reviving in {hero.respawn_timer_ms / 1000.0:.1f}s",
                font=game_scene.font_small,
            )

    @staticmethod
    def _draw_spell_button(
        surface: pygame.Surface,
        game_scene: Any,
        rect: pygame.Rect,
        spell_key: str,
        title: str,
        hotkey: str,
        cd_ms: float,
        max_cd_ms: float,
        accent: Tuple[int, int, int],
        mouse_pos: Tuple[int, int],
    ) -> None:
        s = game_scene.ui_scale
        ready = cd_ms <= 0.0
        hov = rect.collidepoint(mouse_pos) and ready
        border = pal.GOLD_SHINE if hov else (accent if ready else pal.STONE_DARK)
        bg = pal.UI_BG_MID if ready else (24, 22, 32)
        draw_pixel_panel(surface, rect, bg_color=bg, border_color=border, gold_corners=False)

        ic = game_scene.pixel_gen.get_icon(spell_key)
        surface.blit(ic, (rect.left + int(10 * s), rect.centery - ic.get_height() // 2))

        tx = rect.left + int(42 * s)
        draw_text_shadow(
            surface,
            game_scene.font_small,
            f"[{hotkey}] {title}",
            pal.UI_TEXT_WHITE if ready else pal.UI_TEXT_MUTED,
            pos=(tx, rect.top + int(15 * s)),
            align="midleft",
        )
        if ready:
            draw_text_shadow(
                surface,
                game_scene.font_small,
                "READY!",
                pal.GOLD_SHINE,
                pos=(tx, rect.bottom - int(14 * s)),
                align="midleft",
            )
        else:
            bar_r = pygame.Rect(tx, rect.bottom - int(19 * s), rect.width - int(52 * s), int(12 * s))
            ratio = 1.0 - (cd_ms / max(1.0, float(max_cd_ms)))
            draw_pixel_bar(
                surface,
                bar_r,
                ratio,
                fill_color=accent,
                label=f"{cd_ms / 1000.0:.1f}s",
                font=game_scene.font_small,
            )
