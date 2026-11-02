from __future__ import annotations
from typing import Dict, Tuple, Any
import pygame
from core.config import DIFFICULTY_PROFILES, BIOME_DEFINITIONS
from core.events import (
    Event,
    EVENT_UI_CLICK,
    EVENT_QUIT,
    EVENT_SOUND_VOLUME_CHANGED,
    EVENT_MUSIC_VOLUME_CHANGED,
    EVENT_SOUND_TOGGLE,
)
from graphics import palette as pal
from graphics.ui_kit import draw_pixel_panel, draw_pixel_button, draw_pixel_bar, draw_text_shadow


class MenuSystem:
    """Renders procedural pixel-art Main Menu, Settings Menu, Pause, Victory, and Game Over screens."""

    def __init__(self) -> None:
        self.rects: Dict[str, pygame.Rect] = {}

    # ------------------------------------------------------------------
    # MAIN MENU
    # ------------------------------------------------------------------
    def draw_main_menu(self, surface: pygame.Surface, game: Any) -> None:
        s = game.ui_scale
        w, h = game.width, game.height
        mx, my = pygame.mouse.get_pos()
        self.rects.clear()

        # Dimmed battlefield backdrop
        if game.map_surface:
            surface.blit(game.map_surface, (0, 0))
        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((12, 10, 22, 150))
        surface.blit(dim, (0, 0))

        # Royal Center Card
        card = pygame.Rect(0, 0, int(540 * s), int(530 * s))
        card.center = (w // 2, h // 2)
        draw_pixel_panel(surface, card, bg_color=pal.UI_BG_DARK, border_color=pal.UI_BORDER_GOLD)

        # Title Header Banner
        banner = pygame.Rect(0, 0, int(480 * s), int(76 * s))
        banner.centerx = card.centerx
        banner.top = card.top + int(22 * s)
        draw_pixel_panel(surface, banner, bg_color=pal.ROYAL_BLUE_DARK, border_color=pal.GOLD_SHINE)
        draw_text_shadow(
            surface,
            game.font_big,
            "TOWER DEFENSE II",
            pal.GOLD_SHINE,
            pos=(banner.centerx, banner.top + int(27 * s)),
        )
        draw_text_shadow(
            surface,
            game.font_small,
            "ROYAL GUARD — TACTICAL PIXEL EDITION",
            pal.UI_TEXT_WHITE,
            pos=(banner.centerx, banner.bottom - int(18 * s)),
        )

        # Showcase the 4 procedural pixel tower turrets + Royal Paladin Hero
        showcase_y = banner.bottom + int(32 * s)
        t_keys = ["archer", "artillery", "frost", "lightning"]
        anim_tick = (pygame.time.get_ticks() // 220) % 4
        for i, tk in enumerate(t_keys):
            tx = card.centerx + int((i - 2.0) * 86 * s)
            base_srf = game.pixel_gen.get_tower_base(tk, 3)
            tur_srf = game.pixel_gen.get_tower_turret(tk, 3, -45.0, anim_tick)
            surface.blit(base_srf, base_srf.get_rect(center=(tx, showcase_y + int(4 * s))))
            surface.blit(tur_srf, tur_srf.get_rect(center=(tx, showcase_y - int(10 * s))))

        hero_tx = card.centerx + int(2.0 * 86 * s)
        hero_srf = game.pixel_gen.get_hero_sprite(walk_frame=anim_tick, attack_frame=0, level=5)
        surface.blit(hero_srf, hero_srf.get_rect(center=(hero_tx, showcase_y - int(2 * s))))

        # Best Score & Wave Record
        best_wave = game.settings.get("best_wave", 1)
        high_score = game.settings.get("high_score", 0)
        draw_text_shadow(
            surface,
            game.font_small,
            f"High Score: {high_score}   |   Best Wave: {best_wave}",
            pal.GOLD_LIGHT,
            pos=(card.centerx, showcase_y + int(46 * s)),
        )

        # Menu Buttons
        btn_w, btn_h = int(340 * s), int(42 * s)
        y0 = showcase_y + int(80 * s)
        gap = int(50 * s)

        play_r = pygame.Rect(0, 0, btn_w, btn_h)
        play_r.center = (card.centerx, y0)
        self.rects["menu_play"] = play_r
        draw_pixel_button(
            surface,
            play_r,
            "START BATTLE",
            game.font_mid,
            hovered=play_r.collidepoint(mx, my),
            accent_color=pal.ARCHER_GREEN_DARK,
        )

        biome_key = game.settings.get("biome", "grasslands")
        biome_cfg = BIOME_DEFINITIONS.get(biome_key, BIOME_DEFINITIONS["grasslands"])
        biome_r = pygame.Rect(0, 0, btn_w, btn_h)
        biome_r.center = (card.centerx, y0 + gap)
        self.rects["menu_biome"] = biome_r
        draw_pixel_button(
            surface,
            biome_r,
            f"BIOME: {biome_cfg['name'].upper()}",
            game.font_small,
            hovered=biome_r.collidepoint(mx, my),
            accent_color=pal.UI_BG_MID,
        )

        diff_key = game.settings.get("difficulty", "normal")
        diff_label = DIFFICULTY_PROFILES.get(diff_key, DIFFICULTY_PROFILES["normal"])["label"]
        diff_r = pygame.Rect(0, 0, btn_w, btn_h)
        diff_r.center = (card.centerx, y0 + gap * 2)
        self.rects["menu_difficulty"] = diff_r
        draw_pixel_button(
            surface,
            diff_r,
            f"DIFFICULTY: {diff_label.upper()}",
            game.font_mid,
            hovered=diff_r.collidepoint(mx, my),
        )

        set_r = pygame.Rect(0, 0, btn_w, btn_h)
        set_r.center = (card.centerx, y0 + gap * 3)
        self.rects["menu_settings"] = set_r
        draw_pixel_button(
            surface,
            set_r,
            "SETTINGS",
            game.font_mid,
            hovered=set_r.collidepoint(mx, my),
        )

        quit_r = pygame.Rect(0, 0, btn_w, btn_h)
        quit_r.center = (card.centerx, y0 + gap * 4)
        self.rects["menu_quit"] = quit_r
        draw_pixel_button(
            surface,
            quit_r,
            "QUIT GAME",
            game.font_mid,
            hovered=quit_r.collidepoint(mx, my),
            accent_color=pal.CRIMSON_DARK,
        )

    def handle_main_menu_click(self, pos: Tuple[int, int], game: Any) -> None:
        if self.rects.get("menu_play") and self.rects["menu_play"].collidepoint(pos):
            game.ev_manager.post(Event(EVENT_UI_CLICK))
            game.reset_battle()
            game.change_state("playing")
        elif self.rects.get("menu_biome") and self.rects["menu_biome"].collidepoint(pos):
            game.ev_manager.post(Event(EVENT_UI_CLICK))
            order = list(BIOME_DEFINITIONS.keys())
            cur = game.settings.get("biome", "grasslands")
            nxt = order[(order.index(cur) + 1) % len(order)] if cur in order else "grasslands"
            game.settings["biome"] = nxt
            game.rebake_biome_map()
            game.persist_settings()
        elif self.rects.get("menu_difficulty") and self.rects["menu_difficulty"].collidepoint(pos):
            game.ev_manager.post(Event(EVENT_UI_CLICK))
            order = ["easy", "normal", "hard"]
            cur = game.settings.get("difficulty", "normal")
            nxt = order[(order.index(cur) + 1) % len(order)] if cur in order else "normal"
            game.settings["difficulty"] = nxt
            game.persist_settings()
        elif self.rects.get("menu_settings") and self.rects["menu_settings"].collidepoint(pos):
            game.ev_manager.post(Event(EVENT_UI_CLICK))
            game.settings_return_state = "menu"
            game.change_state("settings")
        elif self.rects.get("menu_quit") and self.rects["menu_quit"].collidepoint(pos):
            game.ev_manager.post(Event(EVENT_UI_CLICK))
            game.ev_manager.post(Event(EVENT_QUIT))

    # ------------------------------------------------------------------
    # SETTINGS MENU
    # ------------------------------------------------------------------
    def draw_settings_menu(self, surface: pygame.Surface, game: Any) -> None:
        s = game.ui_scale
        w, h = game.width, game.height
        mx, my = pygame.mouse.get_pos()
        self.rects.clear()

        if game.map_surface:
            surface.blit(game.map_surface, (0, 0))
        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((12, 10, 22, 175))
        surface.blit(dim, (0, 0))

        card = pygame.Rect(0, 0, int(520 * s), int(450 * s))
        card.center = (w // 2, h // 2)
        draw_pixel_panel(surface, card, bg_color=pal.UI_BG_DARK, border_color=pal.UI_BORDER_GOLD)

        draw_text_shadow(
            surface,
            game.font_big,
            "GAME SETTINGS",
            pal.GOLD_SHINE,
            pos=(card.centerx, card.top + int(38 * s)),
        )

        row_y = card.top + int(95 * s)
        row_gap = int(58 * s)
        btn_w = int(340 * s)
        btn_h = int(42 * s)

        snd_r = pygame.Rect(0, 0, btn_w, btn_h)
        snd_r.center = (card.centerx, row_y)
        self.rects["set_sound_toggle"] = snd_r
        snd_txt = f"AUDIO: {'ON' if game.sound_enabled else 'OFF'}"
        draw_pixel_button(surface, snd_r, snd_txt, game.font_mid, hovered=snd_r.collidepoint(mx, my))

        sfx_r = pygame.Rect(0, 0, btn_w, int(34 * s))
        sfx_r.center = (card.centerx, row_y + row_gap)
        self.rects["set_sfx_bar"] = sfx_r
        draw_pixel_bar(
            surface,
            sfx_r,
            game.sound_volume,
            fill_color=pal.ARCHER_GREEN_MID,
            label=f"SFX Volume: {int(round(game.sound_volume * 100))}% (Click/Drag)",
            font=game.font_small,
        )

        mus_r = pygame.Rect(0, 0, btn_w, int(34 * s))
        mus_r.center = (card.centerx, row_y + row_gap * 2)
        self.rects["set_music_bar"] = mus_r
        draw_pixel_bar(
            surface,
            mus_r,
            game.music_volume,
            fill_color=pal.ROYAL_BLUE_LIGHT,
            label=f"Music Volume: {int(round(game.music_volume * 100))}% (Click/Drag)",
            font=game.font_small,
        )

        if pygame.mouse.get_pressed()[0]:
            if sfx_r.collidepoint(mx, my):
                v = max(0.0, min(1.0, (mx - sfx_r.left) / float(sfx_r.width)))
                game.sound_volume = v
                game.settings["sfx_volume"] = v
                game.ev_manager.post(Event(EVENT_SOUND_VOLUME_CHANGED, data={"volume": v}))
            elif mus_r.collidepoint(mx, my):
                v = max(0.0, min(1.0, (mx - mus_r.left) / float(mus_r.width)))
                game.music_volume = v
                game.settings["music_volume"] = v
                game.ev_manager.post(Event(EVENT_MUSIC_VOLUME_CHANGED, data={"volume": v}))

        fs_r = pygame.Rect(0, 0, btn_w, btn_h)
        fs_r.center = (card.centerx, row_y + row_gap * 3)
        self.rects["set_fullscreen"] = fs_r
        fs_txt = f"FULLSCREEN: {'ON' if game.fullscreen else 'OFF'}"
        draw_pixel_button(surface, fs_r, fs_txt, game.font_mid, hovered=fs_r.collidepoint(mx, my))

        fps_r = pygame.Rect(0, 0, btn_w, btn_h)
        fps_r.center = (card.centerx, row_y + row_gap * 4)
        self.rects["set_fps"] = fps_r
        show_fps = game.settings.get("show_fps", True)
        draw_pixel_button(
            surface,
            fps_r,
            f"FPS COUNTER: {'SHOW' if show_fps else 'HIDE'}",
            game.font_mid,
            hovered=fps_r.collidepoint(mx, my),
        )

        back_r = pygame.Rect(0, 0, int(220 * s), int(44 * s))
        back_r.center = (card.centerx, card.bottom - int(38 * s))
        self.rects["set_back"] = back_r
        draw_pixel_button(
            surface,
            back_r,
            "SAVE & BACK",
            game.font_mid,
            hovered=back_r.collidepoint(mx, my),
            accent_color=pal.GOLD_DARK,
        )

    def handle_settings_click(self, pos: Tuple[int, int], game: Any) -> None:
        if self.rects.get("set_sound_toggle") and self.rects["set_sound_toggle"].collidepoint(pos):
            game.ev_manager.post(Event(EVENT_UI_CLICK))
            game.sound_enabled = not game.sound_enabled
            game.ev_manager.post(Event(EVENT_SOUND_TOGGLE, data={"enabled": game.sound_enabled}))
        elif self.rects.get("set_sfx_bar") and self.rects["set_sfx_bar"].collidepoint(pos):
            r = self.rects["set_sfx_bar"]
            v = max(0.0, min(1.0, (pos[0] - r.left) / float(r.width)))
            game.sound_volume = v
            game.settings["sfx_volume"] = v
            game.ev_manager.post(Event(EVENT_SOUND_VOLUME_CHANGED, data={"volume": v}))
            game.ev_manager.post(Event(EVENT_UI_CLICK))
        elif self.rects.get("set_music_bar") and self.rects["set_music_bar"].collidepoint(pos):
            r = self.rects["set_music_bar"]
            v = max(0.0, min(1.0, (pos[0] - r.left) / float(r.width)))
            game.music_volume = v
            game.settings["music_volume"] = v
            game.ev_manager.post(Event(EVENT_MUSIC_VOLUME_CHANGED, data={"volume": v}))
        elif self.rects.get("set_fullscreen") and self.rects["set_fullscreen"].collidepoint(pos):
            game.ev_manager.post(Event(EVENT_UI_CLICK))
            game.fullscreen = not game.fullscreen
            game.settings["fullscreen"] = game.fullscreen
            game.apply_display_mode()
            game.persist_settings()
        elif self.rects.get("set_fps") and self.rects["set_fps"].collidepoint(pos):
            game.ev_manager.post(Event(EVENT_UI_CLICK))
            game.settings["show_fps"] = not game.settings.get("show_fps", True)
            game.persist_settings()
        elif self.rects.get("set_back") and self.rects["set_back"].collidepoint(pos):
            game.ev_manager.post(Event(EVENT_UI_CLICK))
            game.persist_settings()
            ret = getattr(game, "settings_return_state", "menu")
            game.change_state(ret if ret in ("menu", "paused") else "menu")

    # ------------------------------------------------------------------
    # PAUSE, GAME OVER, AND VICTORY OVERLAYS
    # ------------------------------------------------------------------
    def draw_overlay(self, surface: pygame.Surface, game: Any) -> None:
        if game.state not in ("paused", "game_over", "victory"):
            return
        s = game.ui_scale
        w, h = game.width, game.height
        mx, my = pygame.mouse.get_pos()
        self.rects.clear()

        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((10, 8, 18, 165))
        surface.blit(dim, (0, 0))

        card = pygame.Rect(0, 0, int(420 * s), int(350 * s))
        card.center = (w // 2, h // 2)
        border_col = (
            pal.GOLD_SHINE
            if game.state == "victory"
            else (pal.CRIMSON_LIGHT if game.state == "game_over" else pal.UI_BORDER_GOLD)
        )
        draw_pixel_panel(surface, card, bg_color=pal.UI_BG_DARK, border_color=border_col)

        if game.state == "paused":
            title = "GAME PAUSED"
            sub = f"Wave {game.wave_mgr.current_wave}  |  Score: {game.score}"
            t_col = pal.GOLD_SHINE
        elif game.state == "victory":
            title = "ROYAL VICTORY!"
            sub = f"All 10 Waves Cleared! Score: {game.score}"
            t_col = pal.GOLD_SHINE
        else:
            title = "THE CASTLE HAS FALLEN!"
            sub = f"Reached Wave: {game.wave_mgr.current_wave}  |  Score: {game.score}"
            t_col = pal.UI_RED

        draw_text_shadow(surface, game.font_big, title, t_col, pos=(card.centerx, card.top + int(42 * s)))
        draw_text_shadow(surface, game.font_small, sub, pal.UI_TEXT_WHITE, pos=(card.centerx, card.top + int(78 * s)))

        btn_w, btn_h = int(280 * s), int(42 * s)
        y0 = card.top + int(128 * s)
        gap = int(52 * s)

        if game.state in ("paused", "victory"):
            c_txt = "RESUME" if game.state == "paused" else "CONTINUE ENDLESS MODE"
            cont_r = pygame.Rect(0, 0, btn_w, btn_h)
            cont_r.center = (card.centerx, y0)
            self.rects["ov_continue"] = cont_r
            draw_pixel_button(
                surface,
                cont_r,
                c_txt,
                game.font_mid,
                hovered=cont_r.collidepoint(mx, my),
                accent_color=pal.ARCHER_GREEN_DARK,
            )
            y0 += gap

        rest_r = pygame.Rect(0, 0, btn_w, btn_h)
        rest_r.center = (card.centerx, y0)
        self.rects["ov_restart"] = rest_r
        draw_pixel_button(
            surface,
            rest_r,
            "RESTART BATTLE",
            game.font_mid,
            hovered=rest_r.collidepoint(mx, my),
        )
        y0 += gap

        if game.state == "paused":
            set_r = pygame.Rect(0, 0, btn_w, btn_h)
            set_r.center = (card.centerx, y0)
            self.rects["ov_settings"] = set_r
            draw_pixel_button(
                surface,
                set_r,
                "SETTINGS",
                game.font_mid,
                hovered=set_r.collidepoint(mx, my),
            )
            y0 += gap

        menu_r = pygame.Rect(0, 0, btn_w, btn_h)
        menu_r.center = (card.centerx, y0)
        self.rects["ov_menu"] = menu_r
        draw_pixel_button(
            surface,
            menu_r,
            "MAIN MENU",
            game.font_mid,
            hovered=menu_r.collidepoint(mx, my),
            accent_color=pal.CRIMSON_DARK,
        )

    def handle_overlay_click(self, pos: Tuple[int, int], game: Any) -> None:
        if self.rects.get("ov_continue") and self.rects["ov_continue"].collidepoint(pos):
            game.ev_manager.post(Event(EVENT_UI_CLICK))
            if game.state == "victory":
                game.endless_mode = True
            game.change_state("playing")
        elif self.rects.get("ov_restart") and self.rects["ov_restart"].collidepoint(pos):
            game.ev_manager.post(Event(EVENT_UI_CLICK))
            game.reset_battle()
            game.change_state("playing")
        elif self.rects.get("ov_settings") and self.rects["ov_settings"].collidepoint(pos):
            game.ev_manager.post(Event(EVENT_UI_CLICK))
            game.settings_return_state = "paused"
            game.change_state("settings")
        elif self.rects.get("ov_menu") and self.rects["ov_menu"].collidepoint(pos):
            game.ev_manager.post(Event(EVENT_UI_CLICK))
            game.reset_battle()
            game.change_state("menu")
