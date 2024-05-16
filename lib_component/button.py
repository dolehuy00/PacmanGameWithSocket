import pygame


class Button:

    def __init__(self, text, font, width, height, pos):
        self.pressed = False
        self.font = font

        self.rect = pygame.Rect(pos, (width, height))
        self.color = '#B97A57'

        self.text = text
        self.text_surf = self.font.render(text, True, '#000000')
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

        self.count = 0

    def draw(self, border_radius, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius = border_radius)
        screen.blit(self.text_surf, self.text_rect)
        self.pressed = False
        self.check_click()

    def check_click(self):
        if self.count > 0:
            self.count -= 1
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.color = '#C99B53'
            if pygame.mouse.get_pressed()[0] and self.count == 0:
                self.pressed = True
                self.count = 10
        else:
            self.color = '#B97A57'
            self.pressed = False

