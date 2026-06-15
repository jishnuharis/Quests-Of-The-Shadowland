import pygame
from pygame import mixer

mixer.init()

click_sfx = mixer.Sound("audio/click.mp3")
click_sfx.set_volume(0.5)


class Button:
    def __init__(self, x, y, image, scale=1):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface, play_sfx=True):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True

            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        if action and play_sfx:
            click_sfx.play()
        return action
