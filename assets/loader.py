import os
import sys
import pygame

def load_images(engine):
    base_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    map_path = os.path.join(base_dir, 'assets', 'map.png')
    if os.path.exists(map_path):
        img = pygame.image.load(map_path).convert()
        if img.get_size() != (engine.width, engine.height):
            img = pygame.transform.smoothscale(img, (engine.width, engine.height))
        engine.map_img = img
    tower_path = os.path.join(base_dir, 'assets', 'tower.png')
    enemy_path = os.path.join(base_dir, 'assets', 'enemy.png')
    bullet_path = os.path.join(base_dir, 'assets', 'bullet.png')
    coin_path = os.path.join(base_dir, 'assets', 'coin.png')
    healthbar_path = os.path.join(base_dir, 'assets', 'healthbar.png')
    healthbar_alt_path = os.path.join(base_dir, 'assets', 'health_bar.png')
    coinbar_path = os.path.join(base_dir, 'assets', 'coinbar-fotor-bg-remover-2025112812429.png')
    enemies_counter_path = os.path.join(base_dir, 'assets', 'enemies_counter.png')
    main_menu_path = os.path.join(base_dir, 'assets', 'main_menu.png')
    settings_menu_path = os.path.join(base_dir, 'assets', 'settings_menu.png')
    settings_bg_path = os.path.join(base_dir, 'assets', 'settings.png')
    options_menu_path = os.path.join(base_dir, 'assets', 'options_menu.png')
    volume_up_path = os.path.join(base_dir, 'assets', 'volume_up.png')
    volume_down_path = os.path.join(base_dir, 'assets', 'volume_down.png')
    game_over_path = os.path.join(base_dir, 'assets', 'game_over.png')
    previous_path = os.path.join(base_dir, 'assets', 'previous.png')
    if os.path.exists(tower_path):
        engine.tower_img = pygame.image.load(tower_path).convert_alpha()
    if os.path.exists(enemy_path):
        engine.enemy_img = pygame.image.load(enemy_path).convert_alpha()
    if os.path.exists(bullet_path):
        engine.bullet_img = pygame.image.load(bullet_path).convert_alpha()
    if os.path.exists(coin_path):
        engine.coin_img = pygame.image.load(coin_path).convert_alpha()
    engine.healthbar_imgs = []
    for i in range(6):
        hb = os.path.join(base_dir, 'assets', f'healthbar_{i}.png')
        if os.path.exists(hb):
            engine.healthbar_imgs.append(pygame.image.load(hb).convert_alpha())
    if not engine.healthbar_imgs:
        if os.path.exists(healthbar_path):
            engine.healthbar_img = pygame.image.load(healthbar_path).convert_alpha()
        elif os.path.exists(healthbar_alt_path):
            engine.healthbar_img = pygame.image.load(healthbar_alt_path).convert_alpha()
    if os.path.exists(coinbar_path):
        engine.coinbar_img = pygame.image.load(coinbar_path).convert_alpha()
    if os.path.exists(enemies_counter_path):
        engine.enemies_counter_img = pygame.image.load(enemies_counter_path).convert_alpha()
    if os.path.exists(main_menu_path):
        engine.main_menu_img = pygame.image.load(main_menu_path).convert()
    if os.path.exists(settings_menu_path):
        engine.settings_menu_img = pygame.image.load(settings_menu_path).convert()
    if os.path.exists(options_menu_path):
        engine.options_menu_img = pygame.image.load(options_menu_path).convert()
    if os.path.exists(volume_up_path):
        engine.volume_up_img = pygame.image.load(volume_up_path).convert_alpha()
    if os.path.exists(volume_down_path):
        engine.volume_down_img = pygame.image.load(volume_down_path).convert_alpha()
    if os.path.exists(game_over_path):
        engine.game_over_img = pygame.image.load(game_over_path).convert_alpha()
    else:
        game_over_alt = os.path.join(base_dir, 'assets', 'game_over.PNG')
        if os.path.exists(game_over_alt):
            engine.game_over_img = pygame.image.load(game_over_alt).convert_alpha()
    if os.path.exists(previous_path):
        engine.previous_img = pygame.image.load(previous_path).convert_alpha()

def load_enemy_frames(engine):
    engine.enemy_walk_frames = []
    engine.enemy_attack_frames = []
    engine.boss_frames = []
    base_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    for i in range(1, 5):
        p = os.path.join(base_dir, 'assets', f'enemy_walk_{i}.png')
        if os.path.exists(p):
            engine.enemy_walk_frames.append(pygame.image.load(p).convert_alpha())
    for i in range(1, 5):
        p = os.path.join(base_dir, 'assets', f'enemy_attack_{i}.png')
        if os.path.exists(p):
            engine.enemy_attack_frames.append(pygame.image.load(p).convert_alpha())
    for i in range(0, 8):
        bp = os.path.join(base_dir, 'assets', f'boss_{i}.png')
        if os.path.exists(bp):
            engine.boss_frames.append(pygame.image.load(bp).convert_alpha())
