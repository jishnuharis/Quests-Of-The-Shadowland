import pygame
import os
import pickle
from pygame import mixer
from Button import *

mixer.init()
pygame.init()

clock = pygame.time.Clock()
FPS = 60

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption("Level Editor")

ROWS = 16
MAX_COLS = 160
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = len(os.listdir(f"img/Tile"))
level = 0
l_shift_validity = False
r_ctrl_validity = False
current_tile = 0
prev_tile = current_tile
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1
btn_scroll = 0
btn_scroll_bef_pick = 0
made_change_query = ""
clicked = False

bg_img_list = []
for i in range(11):
    img = pygame.image.load(f"img/Background/{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (1200, SCREEN_HEIGHT))
    bg_img_list.append(img)

image_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f"img/Tile/{x}.png").convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    image_list.append(img)

save_btn_img = pygame.image.load("img/Buttons/save_btn.png").convert_alpha()
load_btn_img = pygame.image.load("img/Buttons/load_btn.png").convert_alpha()

BG = (50, 25, 50)
WHITE = (255, 255, 255)
RED = (255, 25, 25)

FUTURA = pygame.font.SysFont("Futura", 22)

world_data = []


def load_def_world():
    for row in range(ROWS):
        r = [-1] * MAX_COLS
        world_data.append(r)

    for tile in range(0, MAX_COLS):
        world_data[ROWS - 1][tile] = 0
    world_data[4][2] = 15


load_def_world()


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = 1200
    for x, img in enumerate(bg_img_list):
        for i in range(5):
            screen.blit(img, ((i * width) - scroll * x * 0.075, 0))


def draw_grid():
    for col in range(MAX_COLS + 1):
        pygame.draw.line(screen, RED, (col * TILE_SIZE - scroll, 0), (col * TILE_SIZE - scroll, SCREEN_HEIGHT))
    for row in range(ROWS + 1):
        pygame.draw.line(screen, RED, (0, row * TILE_SIZE), (SCREEN_WIDTH, row * TILE_SIZE))


def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                while tile >= TILE_TYPES:
                    tile = TILE_TYPES - 1
                screen.blit(image_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))


save_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 50, save_btn_img)
load_button = Button(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT + LOWER_MARGIN - 50, load_btn_img)

run = True
while run:
    clock.tick(FPS)

    button_list = []
    button_col = 0
    button_row = 0
    for i in range(24):
        if i + btn_scroll < TILE_TYPES:
            tile_button = Button(SCREEN_WIDTH + (75 * button_col) + 50, (75 * button_row) + 50,
                                 image_list[i + btn_scroll])
            button_list.append(tile_button)
            button_col += 1
            if button_col == 3:
                button_col = 0
                button_row += 1

    draw_bg()
    draw_grid()
    draw_world()

    draw_text(f"Level: {level}", FUTURA, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text("Press UP or DOWN Holding Left Shift to Change Level" + made_change_query, FUTURA, WHITE, 10,
              SCREEN_HEIGHT + LOWER_MARGIN - 69)

    if save_button.draw(screen):
        made_change_query = ""
        # click_sfx.play()
        pickle_out = open(f"world_data/level-{level}_data", "wb")
        pickle.dump(world_data, pickle_out)
        pickle_out.close()
    if load_button.draw(screen):
        made_change_query = ""
        # click_sfx.play()
        scroll = 0
        world_data = []
        try:
            pickle_in = open(f"world_data/level-{level}_data", "rb")
            world_data = pickle.load(pickle_in)
            pickle_in.close()
        except Exception:
            load_def_world()

    pygame.draw.rect(screen, BG, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT), 1)

    for btn_count, tile_button in enumerate(button_list):
        if tile_button.draw(screen, False):
            prev_tile = current_tile
            current_tile = btn_count + btn_scroll
            if not clicked:
                click_sfx.play()
                clicked = True
        if prev_tile != current_tile:
            clicked = False

    pygame.draw.rect(screen, RED, button_list[current_tile - btn_scroll].rect, 1)

    if scroll_left:
        scroll = scroll - (7 * scroll_speed) if scroll > 0 else 0
    if scroll_right:
        scroll = scroll + (7 * scroll_speed) if scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH else (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH

    pos = pygame.mouse.get_pos()
    x, y = (pos[0] + scroll) // TILE_SIZE, pos[1] // TILE_SIZE

    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
            made_change_query = "*"
        if pygame.mouse.get_pressed()[1] == 1:
            if world_data[y][x] != -1:
                while world_data[y][x] < btn_scroll:
                    btn_scroll -= 3
                btn_scroll = int(world_data[y][x] // 3) * 3 if world_data[y][x] >= 24 else btn_scroll
                current_tile = world_data[y][x]
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1
            made_change_query = "*"

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_LSHIFT:
                l_shift_validity = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5
            if event.key == pygame.K_RCTRL:
                r_ctrl_validity = True
            if event.key == pygame.K_UP and l_shift_validity:
                level += 1
            if (event.key == pygame.K_DOWN and l_shift_validity) and level >= 0:
                level -= 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_w and btn_scroll > 0:
                btn_scroll -= 3
                if current_tile - btn_scroll >= 24:
                    current_tile -= 3
            if event.key == pygame.K_s and btn_scroll + 3 < TILE_TYPES:
                if abs(current_tile - btn_scroll) <= 2:
                    current_tile += 3
                btn_scroll = min(btn_scroll + 3, TILE_TYPES - 1)
                current_tile = min(current_tile, TILE_TYPES - 1)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                l_shift_validity = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1
            if event.key == pygame.K_RCTRL:
                r_ctrl_validity = False
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False

        if event.type == pygame.MOUSEWHEEL:
            if pos[0] > SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
                if event.y > 0 and btn_scroll > 0:
                    btn_scroll -= 3
                    if current_tile - btn_scroll >= 24:
                        current_tile -= 3
                if event.y < 0 and btn_scroll + 3 < TILE_TYPES:
                    if abs(current_tile - btn_scroll) <= 2:
                        current_tile += 3
                    btn_scroll = min(btn_scroll + 3, TILE_TYPES - 1)
                    current_tile = min(current_tile, TILE_TYPES - 1)
            if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT and r_ctrl_validity:
                if event.y > 0:
                    scroll = scroll - (50 * scroll_speed) if scroll > 0 else 0
                if event.y < 0:
                    scroll = scroll + (50 * scroll_speed) if scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH else (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH

    pygame.display.update()

pygame.quit()
