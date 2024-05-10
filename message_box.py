import pygame
from pygame.locals import *

# pygame.init()
#
# # Màu sắc
# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
#
# # Cài đặt màn hình
# WIDTH, HEIGHT = 800, 600
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
#
# # Cài đặt font
# FONT = pygame.font.Font(None, 30)


class MessageBox:
    def __init__(self, x, y, w, h, background_color, text_color, font, message_spacing, screen):
        self.rect = pygame.Rect(x, y, w, h)
        self.messages = []
        self.offset_y = 0
        self.screen = screen
        self.surface = pygame.Surface((w, h))
        self.background_color = background_color
        self.font = font
        self.text_color = text_color
        self.message_spacing = message_spacing
        self.total_line_count_increase = 0

    def handle_event(self, event):
        # Lấy vị trí con trỏ chuột
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            # xu ly cuon
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    self.scroll(-30)
                elif event.button == 5:  # Scroll down
                    self.scroll(30)

    def add_message(self, message):
        self.messages.append(message)

    def draw(self, your_name):
        self.surface.fill(self.background_color)
        y = 10 - self.offset_y
        total_line_count_increase = 0
        for i, msg in enumerate(self.messages):
            if msg[1] == your_name:
                msg[1] += "(you)"
            message_text = f"{msg[0]} {msg[1]}: {msg[2]}"
            line_count = self.draw_text(self.surface, message_text, self.font, self.text_color,
                                        pygame.Rect(10, y, self.rect.width-10, self.rect.height))
            y += (self.font.get_linesize() * line_count) + self.message_spacing
            total_line_count_increase += line_count - 1
        self.screen.blit(self.surface, self.rect)
        self.total_line_count_increase = total_line_count_increase

    def scroll(self, dy):
        self.offset_y += dy
        self.offset_y = min(self.offset_y,
                            len(self.messages)*(self.font.get_linesize() + self.message_spacing) +
                            (self.font.get_linesize() * self.total_line_count_increase + self.message_spacing) -
                            self.rect.height)
        self.offset_y = max(self.offset_y, 0)

    @staticmethod
    def draw_text(surface, text, font, color, rect):
        y = rect.top
        line_spacing = -2
        line_count = 0

        # Tạo một danh sách các từ từ chuỗi ký tự
        word_list = text.split(' ')

        # Khởi tạo một chuỗi ký tự trống
        line = ''

        for word in word_list:
            test_line = line + word + ' '

            # Kiểm tra xem chuỗi ký tự có vượt quá kích thước chỉ định không
            if font.size(test_line)[0] > rect.width:
                text_surface = font.render(line, True, color)
                surface.blit(text_surface, (rect.left, y))
                y += font.get_height() + line_spacing
                line = word + ' '
                line_count += 1
            else:
                line = test_line

        # Vẽ dòng cuối cùng
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (rect.left, y))
        line_count += 1

        return line_count


# message_box = MessageBox(50, 50, 300, 100, (50, 50, 123), BLACK, FONT, 10, screen)
# message_box.add_message(["10:00", "Nguyen", "Chao ban h awih dwajdj jawd"])
# message_box.add_message(["11:00", "Teo", "Chao ban dwa dwad wad wa"])
# message_box.add_message(["12:00", "Nguyen", "Chao ban adwd wa dwa"])
# message_box.add_message(["13:00", "Huy", "Chao ban"])
# message_box.add_message(["14:00", "Nam", "Chao ban dwa dwa daw"])
# message_box.add_message(["15:00", "Nguyen", "Chao ban"])
# message_box.add_message(["16:00", "Viet", "Chao ban awd awd aw"])
# message_box.add_message(["17:00", "Nguyen", "Chao ban awd wa"])
# message_box.add_message(["18:00", "Tug", "Chao ban"])
#
#
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == QUIT:
#             running = False
#         message_box.handle_event(event)
#
#     screen.fill(WHITE)
#     message_box.draw("Nguyen")
#     pygame.display.flip()
#
# pygame.quit()
