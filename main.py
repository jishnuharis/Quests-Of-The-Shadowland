# import necessary modules
import os
import pygame
import pickle
from decouple import config
from pygame import mixer
from random import randint
from Button import Button
from cryptographer import *

# initialize modules and the screen window
mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Quests Of The Shadowland")

window_icon = pygame.image.load("img/Logo/Icon.png").convert_alpha()
pygame.display.set_icon(window_icon)

clock = pygame.time.Clock()
FPS = 60

# initialize game variables
GRAVITY = 0.75
SCROLL_THRESH = 192
ROWS = 16
COLS = 160
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = len(os.listdir(f"img/Tile"))
MAX_LEVEL = int(decrypt(str(config("MAX_LEVEL"))))
screen_scroll = 0
bg_scroll = 0
level = int(decrypt(str(config("LEVEL"))))
temp_score = 0
high_score = int(decrypt(str(config("HIGH_SCORE"))))
start_game = False
max_level_reached = False
new_high_score = False
start_intro = False
death_sound_played = False
mouse_cursor_visibility = False

# initialize player variable
moving_left = False
moving_right = False
shoot = False
nade = False
nade_thrown = False

# play background music
mixer.music.load("audio/background_music.mp3")
mixer.music.set_volume(0.1)
mixer.music.play(-1, 0.0, 5000)

# load game sound
jump_sfx = mixer.Sound("audio/jump.mp3")
jump_sfx.set_volume(0.2)
landing_sfx = mixer.Sound("audio/landing.mp3")
landing_sfx.set_volume(0.1)
shot_sfx = mixer.Sound("audio/shot.mp3")
shot_sfx.set_volume(0.08)
coin_collect_sfx = mixer.Sound("audio/coin_collect.mp3")
coin_collect_sfx.set_volume(0.1)
explosion_sfx = mixer.Sound("audio/explosion.mp3")
explosion_sfx.set_volume(0.1)
water_splash_sfx = mixer.Sound("audio/water_splash.mp3")
water_splash_sfx.set_volume(0.2)
game_over_sfx = mixer.Sound("audio/game_over.mp3")
game_over_sfx.set_volume(0.4)
level_up_sfx = mixer.Sound("audio/level_up.mp3")
level_up_sfx.set_volume(0.4)
click_sfx = mixer.Sound("audio/click.mp3")
click_sfx.set_volume(0.5)

# load the images
logo_img = pygame.image.load("img/Logo/Title card.png").convert_alpha()

start_btn_img = pygame.image.load("img/Buttons/start_btn.png").convert_alpha()
exit_btn_img = pygame.image.load("img/Buttons/exit_btn.png").convert_alpha()
restart_btn_img = pygame.image.load("img/Buttons/restart_btn.png").convert_alpha()

bg_img_list = []
for i in range(12):
    img = pygame.image.load(f"img/Background/{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (1200, SCREEN_HEIGHT))
    bg_img_list.append(img)

image_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f"img/Tile/{x}.png").convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    image_list.append(img)

bullet_img = pygame.image.load("img/Icons/bullet.png").convert_alpha()
zombie_bullet_img = pygame.image.load("img/Icons/zombie_bullet.png").convert_alpha()
grenade_img = pygame.image.load("img/Icons/grenade.png").convert_alpha()
med_box_img = pygame.image.load("img/Icons/med_kit_box.png").convert_alpha()
ammo_box_img = pygame.image.load("img/Icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("img/Icons/grenade_box.png").convert_alpha()

loot_boxes = {
    "Med-kit": med_box_img,
    "Ammo-kit": ammo_box_img,
    "Grenade-kit": grenade_box_img
}

# game colors
WHITE = (255, 255, 255)
BG = (50, 25, 50)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# game Font
FUTURA = pygame.font.SysFont("FUTURA", 30)


def draw_bg():  # draw background on to the screen
    screen.fill(BG)
    width = 1200
    for x, img in enumerate(bg_img_list):
        for i in range(5):
            screen.blit(img, ((i * width) - bg_scroll * x * 0.075, 0))


def draw_text(text, font, color, x, y, centralize=False):  # draw text on to the screen
    img = font.render(text, True, color)
    img_rect = img.get_rect(center=(SCREEN_WIDTH // 2, y))
    if centralize:
        screen.blit(img, img_rect)
    else:
        screen.blit(img, (x, y))


def reset_game():  # reset the game to start
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    loot_box_group.empty()
    coin_group.empty()
    decoration_group.empty()
    water_group.empty()
    spike_group.empty()
    gate_way_group.empty()

    load_def_world()


class World:  # create world from given data
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    if tile > TILE_TYPES:
                        tile = TILE_TYPES - 1
                    image = image_list[tile]
                    image_rect = image.get_rect()
                    image_rect.x = x * TILE_SIZE
                    image_rect.y = y * TILE_SIZE
                    tile_data = (image, image_rect)
                    if 0 <= tile <= 8:  # obstacles
                        self.obstacle_list.append(tile_data)
                    elif 9 <= tile <= 10:  # water
                        water = Water(x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif 11 <= tile <= 14:  # decorative tiles
                        decoration = Decoration(image, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:  # player
                        player = Soldier("Player", x * TILE_SIZE, y * TILE_SIZE, 1.69, 4, 16, 8)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:  # enemy
                        enemy = Soldier("Enemy", x * TILE_SIZE, y * TILE_SIZE, 1.69, 2, 20, 4)
                        enemy_group.add(enemy)
                    elif tile == 17:  # coin
                        coin = Coin(x * TILE_SIZE, y * TILE_SIZE)
                        coin_group.add(coin)
                    elif tile == 18:  # grenade
                        loot_box = LootBox("Grenade-kit", x * TILE_SIZE, y * TILE_SIZE)
                        loot_box_group.add(loot_box)
                    elif tile == 20:  # ammo
                        loot_box = LootBox("Ammo-kit", x * TILE_SIZE, y * TILE_SIZE)
                        loot_box_group.add(loot_box)
                    elif tile == 19:  # med
                        loot_box = LootBox("Med-kit", x * TILE_SIZE, y * TILE_SIZE)
                        loot_box_group.add(loot_box)
                    elif tile == 21:  # gateway
                        gate_way = GateWay(image, x * TILE_SIZE, y * TILE_SIZE)
                        gate_way_group.add(gate_way)
                    elif tile == 22:  # zombie
                        zombie = Soldier("Zombie", x * TILE_SIZE, y * TILE_SIZE, 1.69, 2, 5, 0)
                        enemy_group.add(zombie)
        return player, health_bar

    def draw(self):  # draw world
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Soldier(pygame.sprite.Sprite):  # create soldier
    def __init__(self, character_type, x, y, scale, speed, ammo, grenade):
        pygame.sprite.Sprite.__init__(self)
        # soldier variables
        self.is_alive = True
        self.character_type = character_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenade = grenade
        self.health = 100
        self.max_health = self.health
        self.score = 0
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.landed = False
        self.flip = False
        self.death_query = "You Died"

        # animation varibles
        self.anime_list = []
        self.frame_index = 0
        self.action_id = 0
        self.update_time = pygame.time.get_ticks()
        anime_types = ["Idle", "Run", "Jump", "Death"]
        for anime in anime_types:
            temp_list = []
            num_of_frames = len(os.listdir(f"img/Characters/{self.character_type}/{anime}"))
            for i in range(num_of_frames):
                img = pygame.image.load(f"img/Characters/{self.character_type}/{anime}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.anime_list.append(temp_list)
        self.image = self.anime_list[self.action_id][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # ai variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, TILE_SIZE * 4, 1)
        self.bite_range = pygame.Rect(0, 0, 16, 1)
        self.bite_cooldown = 0
        self.player_detected = False
        self.bitten = False
        self.idling = False
        self.idling_counter = 0
        self.score_given = False

    def update(self):
        self.update_anime()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        screen_scroll = 0
        dx, dy = 0, 0

        if moving_left:  # moves the player to the left
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:  # moves the player to the right
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump and not self.in_air:  # let the player jump
            jump_sfx.play()
            self.vel_y = -12
            self.in_air = True
            self.landed = False
            self.jump = False

        self.vel_y += GRAVITY
        if self.vel_y > 12:
            self.vel_y = 12
        dy += self.vel_y

        for tile in world.obstacle_list:
            # collision along x axis
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.character_type == 'Enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # collision along y axis
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom - 1
                    self.in_air = False
                    if not self.landed:
                        landing_sfx.play()
                    self.landed = True

        # check collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            water_splash_sfx.play()
            self.death_query = "Aquaphobic Player Fell into Hydrogen oxide"
            self.health = 0

        # check collision with spikes
        for spike in spike_group:
            if spike.sharp_rect.colliderect(self.rect) and self.vel_y > 0:
                self.health -= 20
                self.vel_y = 0
                self.death_query = "Player was spiked"

        # check collision with gate way
        level_complete = False
        if pygame.sprite.spritecollide(self, gate_way_group, False):
            level_complete = True

        # check if player fell out of the world
        if self.rect.top > SCREEN_HEIGHT + 64:
            self.health = 0
            self.death_query = "Player fell out of World"

        # stop player at scroll threshold
        if self.character_type == "Player":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        self.rect.x += dx
        self.rect.y += dy

        # scroll screen along player
        if self.character_type == "Player":
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll <
                (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or \
                    (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self, shooter_type="Soldier"):  # let soldiers shoot bullets
        if self.shoot_cooldown == 0 and self.ammo > 0:
            shot_sfx.play()
            self.shoot_cooldown = 32
            self.ammo -= 1
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), \
                            self.rect.centery, self.direction, shooter_type)
            bullet_group.add(bullet)

    def ai(self):  # makes enemies do somethings
        self.line = (player.rect.center, self.rect.center)
        self.collide_point = True if any(tile[1].clipline(self.line) for tile in world.obstacle_list) else False
        if self.is_alive and player.is_alive:
            self.vision.center = (
                self.rect.centerx + screen_scroll + (TILE_SIZE * 2 + 28) * self.direction, self.rect.centery)
            self.bite_range.center = (self.rect.centerx + screen_scroll + 28 * self.direction, self.rect.centery)
            # makes enemies idle
            if not self.idling and randint(1, 192) == 69:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 64
            if self.bite_cooldown > 0:
                self.bite_cooldown -= 1
                if self.bite_cooldown == 0:
                    self.bitten = False
            if self.vision.colliderect(player.rect) and not self.ammo and self.character_type == "Zombie":
                self.idling = False
                self.player_detected = True
            else:
                self.player_detected = False
            if self.bite_range.colliderect(player.rect) and not self.ammo and self.character_type == "Zombie":
                self.update_action(0)
                self.idling = True
                if not self.bitten:
                    player.health -= 20
                    if player.health <= 0:
                        player.death_query = "Player was Bitten to Death by Zombie"
                    self.bitten = True
                    self.bite_cooldown = 72
            # check if player is in range
            elif self.vision.colliderect(player.rect) and self.ammo > 0 and not self.collide_point:
                self.update_action(0)
                self.shoot("Zombie" if self.character_type == "Zombie" else "Soldier")
            else:
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    if self.move_counter > TILE_SIZE and not self.player_detected:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        # changes enemies' state to idle when player is dead
        if not player.is_alive and self.is_alive:
            self.update_action(0)

        self.rect.x += screen_scroll

    def update_anime(self):  # update the animation of the character
        ANIME_COOLDOWN = 100

        self.image = self.anime_list[self.action_id][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIME_COOLDOWN:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
            if self.frame_index == len(self.anime_list[self.action_id]):
                self.frame_index = 0
                if self.action_id == 3:
                    self.frame_index = len(self.anime_list[self.action_id]) - 1

    def update_action(self, new_action_id):  # update the action of the character
        if new_action_id != self.action_id:
            self.action_id = new_action_id
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):  # check if the player is alive
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.is_alive = False
            self.update_action(3)  # Death

    def draw(self):  # draw the character on to the screen
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class GateWay(pygame.sprite.Sprite):  # create gate way to the next level
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + TILE_SIZE - self.image.get_height())

    def update(self):
        self.rect.x += screen_scroll


class Coin(pygame.sprite.Sprite):  # create coins
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.anime_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        for i in range(6):
            img = pygame.image.load(f"img/Coin/{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            self.anime_list.append(img)
        self.image = self.anime_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x - 4, y)

    def update_anime(self):  # update the animation of the coin
        ANIME_COOLDOWN = 100

        self.image = self.anime_list[self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIME_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index == len(self.anime_list):
                self.frame_index = 0

    def update(self):
        self.update_anime()
        self.rect.x += screen_scroll
        if self.rect.colliderect(player.rect):
            coin_collect_sfx.play()
            player.score += 10
            self.kill()


class Water(pygame.sprite.Sprite):  # create water
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.anime_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        for i in range(5):
            img = pygame.image.load(f"img/Water/{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            self.anime_list.append(img)
        self.image = self.anime_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update_anime(self):  # update animation of the water
        ANIME_COOLDOWN = 128

        self.image = self.anime_list[self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIME_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index == len(self.anime_list):
                self.frame_index = 0

    def update(self):
        self.update_anime()
        self.rect.x += screen_scroll


class Decoration(pygame.sprite.Sprite):  # create decoratives
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + TILE_SIZE - self.image.get_height())

    def update(self):
        self.rect.x += screen_scroll


class LootBox(pygame.sprite.Sprite):  # create loot boxes
    def __init__(self, loot_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.loot_type = loot_type
        self.image = loot_boxes[self.loot_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            if self.loot_type == "Med-kit":  # create med-kit
                player.health += 32
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.loot_type == "Ammo-kit":  # create ammo-kit
                player.ammo += 16
                if player.ammo > 32:
                    player.ammo = 32
            elif self.loot_type == "Grenade-kit":  # create grenade-kit
                player.grenade += 8
                if player.grenade > 16:
                    player.grenade = 16
            self.kill()


class HealthBar:  # create health bar for player
    def __init__(self, x, y, health, max_health):
        self.x, self.y = x, y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health

        pygame.draw.rect(screen, BLACK, (self.x - 1, self.y - 1, 152, 22))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):  # create bullet
    def __init__(self, x, y, direction, shooter_type="Soldier"):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.shooter_type = shooter_type
        self.image = zombie_bullet_img if self.shooter_type == "Zombie" else bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += self.direction * self.speed + screen_scroll
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:  # kill bullet if it goes out of world
            self.kill()

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):  # kill bullet if it collide with a obstacle
                self.kill()

        if pygame.sprite.spritecollide(player, bullet_group, False):  # drains player's health if it collides with him
            if player.is_alive:
                self.kill()
                player.health = player.health - 5 if self.shooter_type == 'Zombie' else player.health - 10
            if player.health <= 0:
                char_type = "Enemies" if self.shooter_type == "Soldier" else "Zombies"
                player.death_query = "Player was shot by " + char_type
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group,False):  # drains enemies' health if it collides with them
                if enemy.is_alive:
                    self.kill()
                    if self.shooter_type == "Zombie":
                        enemy.health -= 10
                        enemy.score_given = enemy.health <= 0
                    else:
                        enemy.health -= 20
                        if enemy.health <= 0 and not enemy.score_given:
                            player.score += 25
                            enemy.score_given = True


class Grenade(pygame.sprite.Sprite):  # create grenade
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 128
        self.vel_y = -12
        self.speed = 5
        self.image = grenade_img
        self.image = pygame.transform.scale(self.image, (12, 12))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        dx, dy = 0, 0
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        for tile in world.obstacle_list:
            # check collision along x axis
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                self.speed -= 2
                dx = self.direction * self.speed
            # check collision along y axis
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom - 1
                    self.in_air = False

        # invert direction if it goes out of world
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            self.speed -= 1

        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        self.timer -= 1
        if self.timer == 0:  # check if the fuse timer gone off
            self.kill()
            explosion_sfx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 0.5)
            explosion_group.add(explosion)
            # drains health of the one who comes close
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
                if player.health <= 0:
                    player.death_query = "Player was Blown up by a Gerenade"
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50


class Explosion(pygame.sprite.Sprite):  # create explosion
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.frame_index = 0
        for i in range(5):
            img = pygame.image.load(f"img/Explosion/{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        self.counter += 1
        if self.counter == EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index == len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class ScreenFade:  # creates fade
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed

        if self.direction == 1:  # create circular fade
            pygame.draw.rect(screen, self.color, (-self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color,
                             (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, -self.fade_counter * 0.8, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color,
                             (0, SCREEN_HEIGHT // 2 + self.fade_counter * 0.8, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:  # creates linear fade
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, self.fade_counter))

        if self.fade_counter > SCREEN_HEIGHT + 32:
            fade_complete = True

        return fade_complete


# initialize fades
intro_fade = ScreenFade(1, BG, 4)
death_fade = ScreenFade(2, BG, 6)

# initialize buttons
start_button = Button((SCREEN_WIDTH - start_btn_img.get_width() // 2) // 2, SCREEN_HEIGHT // 2 - 20, start_btn_img, 0.5)
exit_button = Button((SCREEN_WIDTH - exit_btn_img.get_width() // 2) // 2, SCREEN_HEIGHT // 2 + 100, exit_btn_img, 0.5)
restart_button = Button(SCREEN_WIDTH // 2 - 86, SCREEN_HEIGHT // 2 - 32, restart_btn_img, 1.69)

# create groups
enemy_group = pygame.sprite.Group()
zombie_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
loot_box_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
gate_way_group = pygame.sprite.Group()

world_data = []


def load_def_world():  # load the default world in the world data
    world_data = []
    for row in range(ROWS):
        r = [-1] * COLS
        world_data.append(r)

    for tile in range(0, COLS):
        world_data[ROWS - 1][tile] = 0
    world_data[4][2] = 15
    return world_data


# create default world if the level doesn't exist
def load_level():
    try:
        pickle_in = open(f"world_data/level-{level}_data", "rb")
        world_data = pickle.load(pickle_in)
        pickle_in.close()
    except Exception:
        world_data = load_def_world()
    return world_data


world_data = load_level()
world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:
    clock.tick(FPS)

    pygame.mouse.set_visible(mouse_cursor_visibility)

    draw_bg()
    if not start_game:  # generate main menu
        mouse_cursor_visibility = True
        screen.blit(logo_img, ((SCREEN_WIDTH - logo_img.get_width()) // 2, 100))
        if start_button.draw(screen):
            click_sfx.play()
            start_game = True
            start_intro = True
            mouse_cursor_visibility = False
        if exit_button.draw(screen):
            click_sfx.play()
            run = False
    else:
        if level > MAX_LEVEL:
            max_level_reached = True
        if max_level_reached:  # check if max level reached
            mouse_cursor_visibility = True
            screen.blit(logo_img, ((SCREEN_WIDTH - logo_img.get_width()) // 2, 100))
            draw_text("This Level is under Development", FUTURA, WHITE, 0, SCREEN_HEIGHT - 100, True)
            draw_text("Click Start to Startover", FUTURA, WHITE, 0, SCREEN_HEIGHT - 75, True)
            draw_text("Thnx for playin'!", FUTURA, WHITE, 0, SCREEN_HEIGHT - 50, True)
            if start_button.draw(screen):
                level = 1
                overwrite_env(".env", "LEVEL", str(level))
                click_sfx.play()
                max_level_reached = False
                start_game = True
                start_intro = True
                mouse_cursor_visibility = False
                reset_game()
                world_data = load_level()

                world = World()
                player, health_bar = world.process_data(world_data)
            if exit_button.draw(screen):
                run = False
        else:
            world.draw()

            # generate game info on screen
            health_bar.draw(player.health)
            draw_text("AMMO:", FUTURA, WHITE, 10, 35)
            for num in range(player.ammo):
                screen.blit(bullet_img, (90 + (num * 10), 40))
            draw_text("GRENADE:", FUTURA, WHITE, 10, 60)
            for num in range(player.grenade):
                screen.blit(grenade_img, (135 + (num * 15), 60))

            draw_text(f"Level-{level}", FUTURA, WHITE, SCREEN_WIDTH // 2 - 16, 12)
            draw_text(f"Score-{player.score}", FUTURA, WHITE, SCREEN_WIDTH - 128, 12)
            draw_text(f"High Score-{high_score}", FUTURA, WHITE, SCREEN_WIDTH - 177, 35)

            # update all the groups
            bullet_group.update()
            grenade_group.update()
            explosion_group.update()
            loot_box_group.update()
            coin_group.update()
            decoration_group.update()
            water_group.update()
            spike_group.update()
            gate_way_group.update()

            # draw all the groups on the screen
            bullet_group.draw(screen)
            grenade_group.draw(screen)
            explosion_group.draw(screen)
            loot_box_group.draw(screen)
            coin_group.draw(screen)
            decoration_group.draw(screen)
            water_group.draw(screen)
            spike_group.draw(screen)
            gate_way_group.draw(screen)

            # update and draw player on screen
            player.update()
            player.draw()

            # update and draw enemies on screen and let them move
            for enemy in enemy_group:
                enemy.ai()
                enemy.update()
                enemy.draw()

            if start_intro:  # generate a intro fade
                if intro_fade.fade():
                    start_intro = False
                    intro_fade.fade_counter = 0

            if player.is_alive:
                if shoot:
                    player.shoot()
                elif nade and not nade_thrown and player.grenade > 0:
                    grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), \
                                      player.rect.top, player.direction)
                    grenade_group.add(grenade)
                    nade_thrown = True
                    player.grenade -= 1
                if player.in_air:
                    player.update_action(2)  # Jump
                elif moving_left or moving_right:
                    player.update_action(1)  # Run
                else:
                    player.update_action(0)  # Idle
                screen_scroll, level_complete = player.move(moving_left, moving_right)
                bg_scroll -= screen_scroll

                if level_complete:  # check if level has completed
                    level_up_sfx.play()
                    temp_score = player.score
                    start_intro = True
                    bg_scroll = 0
                    reset_game()
                    level += 1
                    if level < MAX_LEVEL:  # check if max level has reached
                        world_data = load_level()

                        world = World()
                        player, health_bar = world.process_data(world_data)

                        player.score = temp_score + 200
                    else:
                        max_level_reached = True
                    overwrite_env(".env", "LEVEL", str(level))
            else:
                if player.score > high_score:
                    new_high_score = True
                    high_score = player.score
                    overwrite_env(".env", "HIGH_SCORE", high_score)
                if not death_sound_played:
                    game_over_sfx.play()
                    death_sound_played = True
                screen_scroll = 0
                if death_fade.fade():  # generate a death fade
                    mouse_cursor_visibility = True

                    # generate death info on screen
                    text_offset = 24 if high_score == player.score and new_high_score else 0
                    draw_text(player.death_query, FUTURA, WHITE, 0, SCREEN_HEIGHT // 2 - 116 - text_offset, True)
                    draw_text(f"Score: {player.score}", FUTURA, WHITE, 0, SCREEN_HEIGHT // 2 - 72 - text_offset, True)
                    draw_text(f"High Score: {high_score}", FUTURA, WHITE, 0, SCREEN_HEIGHT // 2 - 48 - text_offset,
                              True)
                    if text_offset == 24:
                        draw_text("New High Score", FUTURA, WHITE, 0, SCREEN_HEIGHT // 2 - 48, True)

                    if restart_button.draw(screen):
                        mouse_cursor_visibility = False
                        death_sound_played = False
                        click_sfx.play()
                        bg_scroll = 0
                        reset_game()
                        world_data = load_level()
                        world = World()
                        player, health_bar = world.process_data(world_data)
                        death_fade.fade_counter = 0

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w and player.is_alive:
                player.jump = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_e:
                nade = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_e:
                nade = False
                nade_thrown = False

    pygame.display.update()

pygame.quit()
