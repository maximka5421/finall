import pygame as pg
import sys
import os
import random

pg.init()
sc = pg.display.set_mode((800, 800))
pg.display.set_caption("white")
clock = pg.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (100, 149, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
serii = (169, 169, 169)

font = pg.font.SysFont(None, 48)
small_font = pg.font.SysFont(None, 32)

def load_image(path, size=None):
    if not os.path.isfile(path):
        print(f"Файл {path} не найден.")
        sys.exit()
    img = pg.image.load(path).convert_alpha()
    if size:
        img = pg.transform.scale(img, size)
    return img

background = load_image("dark.png", (800, 800))
serii_background = load_image("serii.png", (800, 800))
game_derevo = load_image("derevo.pns.png", (40, 40))
game_derevo.set_colorkey(WHITE)
game_kamen = load_image("kameni.png", (40, 40))
game_kamen.set_colorkey(WHITE)
backgroundgame = load_image("fon.png", (800, 800))
backgroundgame1 = load_image("fon1.png", (800, 800))

player_images = {
    "down": [load_image("zelda.png", (40, 40)), load_image("123.png", (40, 40)), load_image("456.png", (40, 40))],
    "left": [load_image("789 (1).png", (40, 40)), load_image("987.png", (40, 40)), load_image("171819 (1).png", (40, 40))],
    "up": [load_image("101213 (1).png", (40, 40)), load_image("34566 (1).png", (40, 40)), load_image("202122.png", (40, 40))],
    "right": [load_image("232425.png", (40, 40)), load_image("141516.png", (40, 40)), load_image("4455.png", (40, 40))]
}

enemy_images = {
    "down": [load_image("ralevrag1.png", (60, 60)), load_image("ralevrag2.png", (60, 60)), load_image("ralevrag3.png", (60, 60)), load_image("ralevrag4.png", (60, 60))],
    "left": [load_image("ralevrag5.png", (60, 60)), load_image("ralevrag6.png", (60, 60)), load_image("ralevrag7.png", (60, 60)), load_image("ralevrag8.png", (60, 60))],
    "up": [load_image("ralevrag9.png", (60, 60)), load_image("ralevrag10.png", (60, 60)), load_image("ralevrag11.png", (60, 60)), load_image("ralevrag12.png", (60, 60))],
    "right": [load_image("ralevrag13.png", (60, 60)), load_image("ralevrag14.png", (60, 60)), load_image("ralevrag15.png", (60, 60)), load_image("ralevrag16.png", (60, 60))]
}

attack_images = [
    load_image("sword.png", (60, 60)),
    load_image("sworddown.png", (60, 60)),
    load_image("swordleft.png", (60, 60)),
    load_image("swordright.png", (60, 60))
]

arrow_images = {
    "up": load_image("strelaverh.png", (20, 20)),
    "down": load_image("strelavnis.png", (20, 20)),
    "left": load_image("strelawlevo.png", (20, 20)),
    "right": load_image("strelavpravo.png", (20, 20))
}
for img in arrow_images.values():
    img.set_colorkey(WHITE)

current_weapon = "sword"
arrows = []
arrow_speed = 10

def get_attack_offset(direction, distance):
    offsets = {
        "down": (0, distance),
        "up": (0, -distance),
        "left": (-distance, 0),
        "right": (distance, 0),
    }
    return offsets[direction]
attack_duration = 100  # длительность атаки в миллисекундах
attack_timer = 0
attack_active = False
attack_frame_index = 0
attack_animation_timer = 0
attack_animation_speed = 100

in_menu = True
in_settings = False
in_game = False
in_game2 = False
in_rules = False
game_lost = False
game_won = False

button_width = 200
button_height = 60
button_spacing = 20
start_y = 200
buttons = {}
labels = ["грати", "настройки", "правила", "вийти", "грати 2"]
for i, label in enumerate(labels):
    x = (800 - button_width) // 2
    y = start_y + i * (button_height + button_spacing)
    buttons[label] = pg.Rect(x, y, button_width, button_height)

player_rect = pg.Rect(300, 200, 40, 40)
player_speed = 5
player_direction = "down"

enemy_size = 60
enemy_rects = [
    pg.Rect(500, 500, enemy_size, enemy_size),
    pg.Rect(100, 600, enemy_size, enemy_size),
    pg.Rect(600, 100, enemy_size, enemy_size),
]
enemy_speeds = [2, 1.8, 2.2]
enemy_directions = [pg.Vector2(1, 0) for _ in range(3)]
target_directions = [pg.Vector2(1, 0) for _ in range(3)]
change_direction_timers = [0, 0, 0]
enemy_animation_indices = [0, 0, 0]
enemy_animation_timers = [0, 0, 0]
enemy_animation_speed = 150
enemy_health = [3, 3, 3]

tree_count = 30
tree_rects = []
for _ in range(tree_count):
    x = random.randint(0, sc.get_width() - 40)
    y = random.randint(0, sc.get_height() - 40)
    rect = pg.Rect(x, y, 40, 40)
    while rect.colliderect(player_rect):
        x = random.randint(0, sc.get_width() - 40)
        y = random.randint(0, sc.get_height() - 40)
        rect.topleft = (x, y)
    tree_rects.append(rect)

animation_index = 0
animation_timer = 0
animation_speed = 100

def draw_button(text, rect):
    pg.draw.rect(sc, BLUE, rect)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    sc.blit(text_surf, text_rect)

def reset_game():
    global player_rect, game_lost, game_won, arrows, enemy_health
    player_rect.topleft = (300, 200)
    positions = [(500, 500), (100, 600), (600, 100)]
    for i in range(3):
        enemy_rects[i].topleft = positions[i]
    game_lost = False
    game_won = False
    arrows = []
    enemy_health = [3 for _ in enemy_rects]

def get_enemy_direction(enemy_vector):
    if enemy_vector.x > 0:
        return "right"
    elif enemy_vector.x < 0:
        return "left"
    elif enemy_vector.y > 0:
        return "down"
    elif enemy_vector.y < 0:
        return "up"
    return "down"

def check_collision_with_trees(enemy_rect, tree_rects):
    for tree_rect in tree_rects:
        if enemy_rect.colliderect(tree_rect):
            return True
    return False


# --- Игровой цикл ---
while True:
    delta_time = clock.tick(FPS)
    pg.display.set_caption(str(int(clock.get_fps())))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if in_menu and event.type == pg.MOUSEBUTTONDOWN:
            if buttons["грати"].collidepoint(event.pos):
                in_menu, in_game = False, True
                reset_game()
            elif buttons["настройки"].collidepoint(event.pos):
                in_menu, in_settings = False, True
            elif buttons["правила"].collidepoint(event.pos):
                in_menu, in_rules = False, True
            elif buttons["вийти"].collidepoint(event.pos):
                pg.quit()
                sys.exit()
            elif buttons["грати 2"].collidepoint(event.pos):
                in_menu, in_game2 = False, True
                reset_game()
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            if in_settings or in_rules or in_game or game_lost:
                in_menu = True
                in_settings = in_rules = in_game = game_lost = game_won = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_1:
                current_weapon = "sword"
            elif event.key == pg.K_2:
                current_weapon = "bow"
        elif event.type == pg.MOUSEBUTTONDOWN and (in_game or in_game2):
            if current_weapon == "sword":
                attack_active = True
                attack_timer = attack_duration
            elif current_weapon == "bow":
                offset_x, offset_y = get_attack_offset(player_direction, 40)
                arrow_rect = arrow_images[player_direction].get_rect(center=(player_rect.centerx + offset_x, player_rect.centery + offset_y))
                arrows.append({"rect": arrow_rect, "dir": player_direction})

    # --- Рендер ---
    if in_menu or in_settings or in_rules:
        sc.blit(background, (0, 0))
    else:
        sc.fill(GREEN)

    if in_menu:
        for name, rect in buttons.items():
            draw_button(name, rect)

    elif in_settings:
        sc.blit(font.render("Настройки (ESC - назад)", True, BLACK), (50, 180))

    elif in_rules:
        rules = [
            "Правила игры:",
            "1. WASD - движение.",
            "2. Мышь - атака.",
            "3. 1 - меч, 2 - лук.",
            "4. ESC - меню.",
        ]
        for i, line in enumerate(rules):
            sc.blit(small_font.render(line, True, BLACK), (50, 100 + i * 40))

    elif in_game or in_game2:
        
        if in_game2:
            sc.blit(backgroundgame1, (0, 0))
        else:
            sc.blit(backgroundgame, (0, 0))

        # --- движение игрока ---
        keys = pg.key.get_pressed()
        moving = False
        old_position = player_rect.topleft

        if not game_lost and not game_won:
            if keys[pg.K_a]:
                player_rect.x -= player_speed
                moving = True
                player_direction = "left"
            elif keys[pg.K_d]:
                player_rect.x += player_speed
                moving = True
                player_direction = "right"
            elif keys[pg.K_w]:
                player_rect.y -= player_speed
                moving = True
                player_direction = "up"
            elif keys[pg.K_s]:
                player_rect.y += player_speed
                moving = True
                player_direction = "down"

            for tree_rect in tree_rects:
                if player_rect.colliderect(tree_rect):
                    player_rect.topleft = old_position
                    moving = False
                    break

            for rect in enemy_rects:
                if player_rect.colliderect(rect):
                    game_lost = True
                    break

            if moving:
                animation_timer += delta_time
                if animation_timer >= animation_speed:
                    animation_timer = 0
                    animation_index = (animation_index + 1) % len(player_images[player_direction])
            else:
                animation_index = 0

            player_rect.clamp_ip(sc.get_rect())

        sc.blit(player_images[player_direction][animation_index], player_rect.topleft)

        # --- атака мечом ---
        if attack_active and current_weapon == "sword":
            attack_distance = 30
            offset_x, offset_y = get_attack_offset(player_direction, attack_distance)
            if player_direction == "up":
                attack_image = attack_images[0]
            elif player_direction == "down":
                attack_image = attack_images[1]
            elif player_direction == "left":
                attack_image = attack_images[2]
            else:
                attack_image = attack_images[3]

            attack_rect = attack_image.get_rect(center=(player_rect.centerx + offset_x, player_rect.centery + offset_y))
            sc.blit(attack_image, attack_rect.topleft)

            for i in range(len(enemy_rects)-1, -1, -1):
                if attack_rect.colliderect(enemy_rects[i]):
                    enemy_health[i] -= 1
                    if enemy_health[i] <= 0:
                        del enemy_rects[i]
                        del enemy_speeds[i]
                        del enemy_directions[i]
                        del target_directions[i]
                        del change_direction_timers[i]
                        del enemy_animation_indices[i]
                        del enemy_animation_timers[i]
                        del enemy_health[i]

            attack_timer -= delta_time
            if attack_timer <= 0:
                attack_active = False

            if not enemy_rects:
                game_won = True

        # --- стрелы ---
        for arrow in arrows[:]:
            if arrow["dir"] == "up":
                arrow["rect"].y -= arrow_speed
            elif arrow["dir"] == "down":
                arrow["rect"].y += arrow_speed
            elif arrow["dir"] == "left":
                arrow["rect"].x -= arrow_speed
            elif arrow["dir"] == "right":
                arrow["rect"].x += arrow_speed

            sc.blit(arrow_images[arrow["dir"]], arrow["rect"].topleft)

            if not sc.get_rect().colliderect(arrow["rect"]):
                arrows.remove(arrow)
                continue

            for i in range(len(enemy_rects)-1, -1, -1):
                if arrow["rect"].colliderect(enemy_rects[i]):
                    enemy_health[i] -= 1
                    if enemy_health[i] <= 0:
                        del enemy_rects[i]
                        del enemy_speeds[i]
                        del enemy_directions[i]
                        del target_directions[i]
                        del change_direction_timers[i]
                        del enemy_animation_indices[i]
                        del enemy_animation_timers[i]
                        del enemy_health[i]
                    arrows.remove(arrow)
                    break

            if not enemy_rects:
                game_won = True

        # --- деревья ---
        for tree_rect in tree_rects:
            if in_game2:
                sc.blit(game_kamen, tree_rect.topleft)
            else:
                sc.blit(game_derevo, tree_rect.topleft)

        # --- враги ---
        if not game_lost and not game_won:
            for i in range(len(enemy_rects)):
                change_direction_timers[i] += delta_time
                if change_direction_timers[i] > 1500:
                    change_direction_timers[i] = 0
                    dx = random.uniform(-1, 1)
                    dy = random.uniform(-1, 1)
                    if dx != 0 or dy != 0:
                        target_directions[i] = pg.Vector2(dx, dy).normalize()

                if check_collision_with_trees(enemy_rects[i], tree_rects):
                    target_directions[i] = pg.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()

                enemy_directions[i] = enemy_directions[i].lerp(target_directions[i], 0.05)
                enemy_rects[i].x += enemy_directions[i].x * enemy_speeds[i]
                enemy_rects[i].y += enemy_directions[i].y * enemy_speeds[i]

                enemy_rects[i].clamp_ip(sc.get_rect())

                enemy_animation_timers[i] += delta_time
                if enemy_animation_timers[i] >= enemy_animation_speed:
                    enemy_animation_timers[i] = 0
                    enemy_animation_indices[i] = (enemy_animation_indices[i] + 1) % len(enemy_images[get_enemy_direction(enemy_directions[i])])

                sc.blit(enemy_images[get_enemy_direction(enemy_directions[i])][enemy_animation_indices[i]], enemy_rects[i].topleft)

                pg.draw.rect(sc, RED, (enemy_rects[i].x, enemy_rects[i].y - 10, enemy_rects[i].width, 5))
                health_ratio = enemy_health[i] / 3
                pg.draw.rect(sc, GREEN, (enemy_rects[i].x, enemy_rects[i].y - 10, enemy_rects[i].width * health_ratio, 5))

        if game_lost:
            sc.blit(font.render("Вы проиграли! (ESC - назад)", True, BLACK), (50, 350))

        if game_won and not game_lost:
            sc.blit(font.render("Вы победили! (ESC - назад)", True, BLACK), (50, 350))

    pg.display.update()


