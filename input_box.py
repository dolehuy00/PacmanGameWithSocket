
import pygame


# class o nhap lieu
class InputBox:
    def __init__(self, x, y, w, text, limit_text, font, text_color, color_inactive, color_active, border_radius):
        self.y = y
        self.rect = pygame.Rect(x, y, w, font.get_height() * 2 + 10)
        self.color = color_inactive
        self.text = text
        self.txt_surface = font.render(text, True, text_color)
        self.active = False
        self.font = font
        self.colorChange = color_active
        self.text_color = text_color
        self.border_radius = border_radius
        self.defaultBorderColor = color_inactive
        self.limit_text = limit_text
        self.rect.y = self.y - self.font.get_height()

    def handle_event(self, event, event_enter_callback):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.colorChange if self.active else self.defaultBorderColor
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    event_enter_callback(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if not len(self.text) == self.limit_text:
                        self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.text_color)

    def draw_wrapped_text(self, surface, text, x, y, max_width):
        words = text.split()
        lines = []
        current_line = ''

        for word in words:
            test_line = current_line + ' ' + word if current_line else word
            test_rect = self.font.render(test_line, True, self.text_color).get_rect()

            if test_rect.width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)

        for line in lines:
            text_surface = self.font.render(line, True, self.text_color)
            surface.blit(text_surface, (x, y))
            y += self.font.get_linesize()

    def draw(self, screen):
        self.draw_wrapped_text(screen, self.text, self.rect.x + 5, self.rect.y + 5, self.rect.w-5)
        pygame.draw.rect(screen, self.color, self.rect, 2, self.border_radius)
