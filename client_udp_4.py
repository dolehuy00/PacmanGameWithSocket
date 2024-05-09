import copy
from map import map_level_1
import pygame
import random
import socket
import threading
import json

# Tạo socket client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 12345)

# nickname
nick_name = "Client 4"

# init pygame
pygame.init()

# đặt kích thước các màn hình
WIDTH_PLAYING = 900
HEIGHT_PLAYING = 750

WIDTH_SCREEN = 1200
HEIGHT_SCREEN = 750

HEIGHT_SCORE_TABLE = 300
WIDTH_SCORE_TABLE = 300

HEIGHT_BOX_CHAT = 450
WIDTH_BOX_CHAT = 300

screen = pygame.display.set_mode([WIDTH_SCREEN, HEIGHT_SCREEN])

# đặt tên cho cửa sổ
pygame.display.set_caption("Pacman")

# đặt icon cho cửa sổ
icon = pygame.image.load("images/pacman/1.png")
pygame.display.set_icon(icon)


# thông tin map
map_level = copy.deepcopy(map_level_1)

# thông tin fps
timer = pygame.time.Clock()
fps = 60

# tải phông chữ
font_regular_path = "font/Roboto/Roboto-Regular.ttf"
font_bold_part = "font/Roboto/Roboto-Bold.ttf"
font = pygame.font.Font(font_regular_path, 20)

# màu nền
background_color = (45, 45, 45)

# tải ảnh pacman
player_images = []
for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f"images/pacman/{i}.png"), (25, 25)))

# tải hình ảnh mấy con ma
blue_ghost_image = pygame.transform.scale(pygame.image.load("images/ghost/blue.png"), (25, 25))
pink_ghost_image = pygame.transform.scale(pygame.image.load("images/ghost/pink.png"), (25, 25))
red_ghost_image = pygame.transform.scale(pygame.image.load("images/ghost/red.png"), (25, 25))
orange_ghost_image = pygame.transform.scale(pygame.image.load("images/ghost/orange.png"), (25, 25))
ghost_slow_image = pygame.transform.scale(pygame.image.load("images/ghost/powerUp.png"), (25, 25))
dead_ghost_image = pygame.transform.scale(pygame.image.load("images/ghost/dead.png"), (25, 25))

# tải hình ảnh tường
wall_3 = pygame.transform.scale(pygame.image.load("images/wall/3.png"), (25, 25))
wall_4 = pygame.transform.scale(pygame.image.load("images/wall/4.png"), (25, 25))
wall_5 = pygame.transform.scale(pygame.image.load("images/wall/5.png"), (25, 25))
wall_6 = pygame.transform.scale(pygame.image.load("images/wall/6.png"), (25, 25))
wall_7 = pygame.transform.scale(pygame.image.load("images/wall/7.png"), (25, 25))
wall_8 = pygame.transform.scale(pygame.image.load("images/wall/8.png"), (25, 25))

# tải hình ảnh thức ăn
small_food = pygame.transform.scale(pygame.image.load("images/food/small_dot.png"), (25, 25))
big_food = pygame.transform.scale(pygame.image.load("images/food/big_dot.png"), (25, 25))

# tai hinh anh khung score
score_board_frame = pygame.transform.scale(pygame.image.load("images/score/score_table.png"), (WIDTH_SCORE_TABLE, HEIGHT_SCORE_TABLE))

# cài đặt thông tin thức ăn nhấp nháy
flicker_food = False
loop_flicker_food_clock = 0


# tìm vị trí trống trong matrix map
def random_empty_position_in_map(matrix):
    empty_positions = [(y, x) for y in range(len(matrix) - 1) for x in range(len(matrix[0]) - 1) if matrix[y][x] == 0]
    if empty_positions:
        return random.choice(empty_positions)
    else:
        return None


# random và tính toán vị trí trống
def random_empty_position(matrix):
    y, x = random_empty_position_in_map(matrix)
    return x * 25, y * 25


# thông tin mấy con ma
ghost_is_slow = False
ghost_slow_time_count = 0
ghost_slow_time_default = 600

red_ghost_x = 1 * 25
red_ghost_y = 1 * 25
red_ghost_direction = 0
red_ghost_dead = False
red_dead_time_count = 0
red_dead_time_default = 400
flicker_red_ghost_clock = 0

blue_ghost_x = 1 * 25
blue_ghost_y = 1 * 25
blue_ghost_direction = 1
blue_ghost_dead = False
blue_dead_time_count = 0
blue_dead_time_default = 400
flicker_blue_ghost_clock = 0

orange_ghost_x = 1 * 25
orange_ghost_y = 1 * 25
orange_ghost_direction = 2
orange_ghost_dead = False
orange_dead_time_count = 0
orange_dead_time_default = 400
flicker_orange_ghost_clock = 0

pink_ghost_x = 1 * 25
pink_ghost_y = 1 * 25
pink_ghost_direction = 3
pink_ghost_dead = False
pink_dead_time_count = 0
pink_dead_time_default = 400
flicker_pink_ghost_clock = 0

ghost_speeds_default = [3, 2, 2, 2]
ghost_speeds = ghost_speeds_default

# thông tin player
center_player_x = 0
center_player_y = 0
player_direction = 0
loop_count_player = 0
speed_player = 2
turns_allowed = [False, False, False, False]  # Right, Left, Up, Down
player_dead = True
total_score = 0
is_flickering_player = False
is_visible_player = False
count_flicker_player = 0
player_flicker_time_default = 200
player_flicker_time_count = player_flicker_time_default
font_name_player = pygame.font.Font(font_regular_path, 12)

# thoong tin cacs nguoi choi khac
other_player_data = []

# thong tin bang xep hang
data_score_table = {}
text_score_color = (112, 74, 53)


# hàm nhận dữ liệu từ server
def receive_data():
    global red_ghost_x, red_ghost_y, red_ghost_direction, red_ghost_dead, red_dead_time_count, red_dead_time_default, \
        blue_ghost_x, blue_ghost_y, blue_ghost_direction, blue_ghost_dead, blue_dead_time_count, \
        blue_dead_time_default, orange_ghost_x, orange_ghost_y, orange_ghost_direction, orange_ghost_dead,\
        orange_dead_time_count, orange_dead_time_default, pink_ghost_x, pink_ghost_y, pink_ghost_direction, \
        pink_ghost_dead, pink_dead_time_count, pink_dead_time_default, ghost_speeds, map_level, player_dead, \
        player_x, player_y, ghost_is_slow, other_player_data, total_score, data_score_table
    while True:
        try:
            # Nhận phản hồi từ server
            response, server_address = client_socket.recvfrom(4096)
            data = json.loads(response.decode())

            data_map = data.get("map")
            if data_map is not None:
                # data map
                map_level = data_map
                # data ghost
                data_ghost = data["ghost"]
                ghost_speeds = data_ghost[24]
                ghost_is_slow = data_ghost[25]
                # data red ghost
                red_ghost_x = data_ghost[0]
                red_ghost_y = data_ghost[1]
                red_ghost_direction = data_ghost[2]
                red_ghost_dead = data_ghost[3]
                red_dead_time_count = data_ghost[4]
                red_dead_time_default = data_ghost[5]
                # data blue ghost
                blue_ghost_x = data_ghost[6]
                blue_ghost_y = data_ghost[7]
                blue_ghost_direction = data_ghost[8]
                blue_ghost_dead = data_ghost[9]
                blue_dead_time_count = data_ghost[10]
                blue_dead_time_default = data_ghost[11]
                # data orange ghost
                orange_ghost_x = data_ghost[12]
                orange_ghost_y = data_ghost[13]
                orange_ghost_direction = data_ghost[14]
                orange_ghost_dead = data_ghost[15]
                orange_dead_time_count = data_ghost[16]
                orange_dead_time_default = data_ghost[17]
                # data pink ghost
                pink_ghost_x = data_ghost[18]
                pink_ghost_y = data_ghost[19]
                pink_ghost_direction = data_ghost[20]
                pink_ghost_dead = data_ghost[21]
                pink_dead_time_count = data_ghost[22]
                pink_dead_time_default = data_ghost[23]

            data_you = data.get("you")
            if data_you is not None:
                total_score = data_you[6]
                if data_you[4]:
                    player_dead = True
                    player_x = data_you[1]
                    player_y = data_you[2]

            data_other_player = data.get("otherPlayer")
            if data_other_player is not None:
                other_player_data = data_other_player

            data_score = data.get("score_table")
            if data_score is not None:
                data_score_table = data_score
                print(data_score_table)

        except Exception as e:
            print("exception", e)


# chạy luồng riêng để nhận dữ liệu
receive_thread = threading.Thread(target=receive_data)
receive_thread.start()

# thông tin vị trí player
player_x, player_y = random_empty_position(map_level)


# hàm vẽ map lên màn hình
def draw_map():
    for i in range(len(map_level)):
        for j in range(len(map_level[i])):
            if map_level[i][j] == 1:
                screen.blit(small_food, (j * 25, i * 25))
            if map_level[i][j] == 2 and not flicker_food:
                screen.blit(big_food, (j * 25, i * 25))
            if map_level[i][j] == 3:
                screen.blit(wall_3, (j * 25, i * 25))
            if map_level[i][j] == 4:
                screen.blit(wall_4, (j * 25, i * 25))
            if map_level[i][j] == 5:
                screen.blit(wall_5, (j * 25, i * 25))
            if map_level[i][j] == 6:
                screen.blit(wall_6, (j * 25, i * 25))
            if map_level[i][j] == 7:
                screen.blit(wall_7, (j * 25, i * 25))
            if map_level[i][j] == 8:
                screen.blit(wall_8, (j * 25, i * 25))


# hàm vẽ player lên màn hình
def draw_player(visible_player, loop_player_clock, player_location_x, player_location_y, direction, name):
    if visible_player:
        name_player = font_name_player.render(name, True, (255, 255, 255), None)
        screen.blit(name_player, name_player.get_rect(center=(player_location_x + 13, player_location_y - 13)))
        # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
        if direction == 0:
            screen.blit(player_images[loop_player_clock // 5], (player_location_x, player_location_y))
        elif direction == 1:
            screen.blit(pygame.transform.flip(
                player_images[loop_player_clock // 5], True, False), (player_location_x, player_location_y))
        elif direction == 2:
            screen.blit(pygame.transform.rotate(
                player_images[loop_player_clock // 5], 90), (player_location_x, player_location_y))
        elif direction == 3:
            screen.blit(pygame.transform.rotate(
                player_images[loop_player_clock // 5], 270), (player_location_x, player_location_y))


# hàm vẽ các player khác
def draw_other_player():
    if len(other_player_data) > 0:
        for other_player in other_player_data:
            draw_player(other_player[7], other_player[8], other_player[1], other_player[2], other_player[3],
                        other_player[0])


# hàm kiểm tra đụng tường
def check_position(location_x, location_y):
    turns = [False, False, False, False]  # Right, Left, Up, Down
    if map_level[location_y // 25][(location_x - speed_player) // 25] < 3:
        turns[1] = True
    if map_level[location_y // 25][(location_x + speed_player + 23) // 25] < 3:
        turns[0] = True
    if map_level[(location_y + speed_player + 23) // 25][location_x // 25] < 3:
        turns[3] = True
    if map_level[(location_y - speed_player) // 25][location_x // 25] < 3:
        turns[2] = True

    return turns


# hàm vẽ tin nhắn
def draw_message(list_message=0):
    pygame.draw.rect(screen, (55, 0, 0), (WIDTH_PLAYING, HEIGHT_SCORE_TABLE, WIDTH_BOX_CHAT, HEIGHT_BOX_CHAT))


# hàm vẽ điểm
def draw_score(data_score):
    screen.blit(score_board_frame, (WIDTH_PLAYING, 0))
    x_left = WIDTH_PLAYING + 30
    y = 90
    x_right = WIDTH_PLAYING + WIDTH_SCORE_TABLE - 30
    count = 1
    for name, score in data_score.items():
        if name == nick_name:
            font_score = pygame.font.Font(font_bold_part, 20)
        else:
            font_score = pygame.font.Font(font_regular_path, 20)
        name_text = font_score.render(str(count) + ". " + name, True, text_score_color, None)
        score_text = font_score.render(str(score), True, text_score_color, None)

        # Lấy kích thước của tên và điểm số
        name_rect = name_text.get_rect(left=x_left, centery=y)
        score_rect = score_text.get_rect(right=x_right, centery=y)

        # Vẽ tên và điểm số
        screen.blit(name_text, name_rect)
        screen.blit(score_text, score_rect)

        # Dịch dòng tiếp theo
        y += font_score.get_height()
        count += 1


# class ghost
class Ghost:
    def __init__(self, x_pos, y_pos, speed, img, direct, dead):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.center_x = self.x_pos + 12
        self.center_y = self.y_pos + 12
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.id = id
        self.turns = [False, False, False, False]  # Right, Left, Up, Down

    def draw(self, count):
        if not ghost_is_slow and not self.dead:
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif ghost_is_slow and not self.dead:
            screen.blit(ghost_slow_image, (self.x_pos, self.y_pos))
        else:
            if count < 40:
                count += 1
                if count > 20:
                    screen.blit(dead_ghost_image, (self.x_pos, self.y_pos))
                else:
                    screen.blit(self.img, (self.x_pos, self.y_pos))
            else:
                count = 0
        return count


# hàm gửi data cho server
def send_data():
    player_dead_default = False
    json_data = json.dumps(
        [nick_name, player_x, player_y, player_direction, player_dead_default, is_flickering_player, total_score,
         is_visible_player, loop_count_player
         ]
    )
    # gửi dữ liệu lên server
    client_socket.sendto(json_data.encode(), server_address)


# game main
game_running = True
while game_running:
    # đặt fps
    timer.tick(fps)

    # nếu player ngủm
    if player_dead and not is_flickering_player:
        is_flickering_player = True

    # thời gian nhấp nháy pacman
    if is_flickering_player and player_flicker_time_count > 0:
        player_flicker_time_count -= 1
        # nhấp nháy pacman
        if count_flicker_player < 10:
            count_flicker_player += 1
            is_visible_player = False
        elif count_flicker_player < 20:
            count_flicker_player += 1
            is_visible_player = True
        else:
            count_flicker_player = 0
    else:
        is_flickering_player = False
        player_dead = False
        is_visible_player = True
        player_flicker_time_count = player_flicker_time_default

    # gửi dữ liệu người chơi lên server
    send_data()

    # nhấp nháy thức ăn lớn
    if loop_flicker_food_clock < 50:
        loop_flicker_food_clock += 1
        # thời gian ẩn
        if loop_flicker_food_clock > 10:
            flicker_food = False
    else:
        loop_flicker_food_clock = 0
        flicker_food = True

    # cơ hàm pacman
    if loop_count_player < 19:
        loop_count_player += 1
    else:
        loop_count_player = 0

    # đặt màu nền
    screen.fill(background_color)

    # Hướng được phép di chuyển của pacman
    turns_allowed = check_position(player_x, player_y)

    #  Đi qua cổng
    if player_x > WIDTH_PLAYING - 30:
        player_x = 15
    if player_x < 5:
        player_x = WIDTH_PLAYING - 30
    if player_y > HEIGHT_PLAYING - 30:
        player_y = 5
    if player_y < 5:
        player_y = HEIGHT_PLAYING - 30

    # gọi hàm vẽ các đối tượng lên màn hình
    # tường
    draw_map()

    # pacman
    draw_player(is_visible_player, loop_count_player, player_x, player_y, player_direction, nick_name)

    draw_other_player()

    # ma đỏ
    red_ghost = Ghost(red_ghost_x, red_ghost_y, ghost_speeds[0], red_ghost_image, red_ghost_direction, red_ghost_dead)
    flicker_red_ghost_clock = red_ghost.draw(flicker_red_ghost_clock)

    # ma xanh
    blue_ghost = Ghost(blue_ghost_x, blue_ghost_y, ghost_speeds[1], blue_ghost_image, blue_ghost_direction,
                       blue_ghost_dead)
    flicker_blue_ghost_clock = blue_ghost.draw(flicker_blue_ghost_clock)

    # ma hồng
    pink_ghost = Ghost(pink_ghost_x, pink_ghost_y, ghost_speeds[2], pink_ghost_image, pink_ghost_direction,
                       pink_ghost_dead)
    flicker_pink_ghost_clock = pink_ghost.draw(flicker_pink_ghost_clock)

    # ma cam
    orange_ghost = Ghost(orange_ghost_x, orange_ghost_y, ghost_speeds[3], orange_ghost_image, orange_ghost_direction,
                         orange_ghost_dead)
    flicker_orange_ghost_clock = orange_ghost.draw(flicker_orange_ghost_clock)

    # score
    draw_score(data_score_table)

    # tin nhắn
    draw_message()

    # sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False

    # Di chuyển player
    key_pressed = pygame.key.get_pressed()
    if key_pressed[pygame.K_w]:
        player_direction = 2
        if turns_allowed[2]:
            player_y -= speed_player
    if key_pressed[pygame.K_s]:
        player_direction = 3
        if turns_allowed[3]:
            player_y += speed_player
    if key_pressed[pygame.K_a]:
        player_direction = 1
        if turns_allowed[1]:
            player_x -= speed_player
    if key_pressed[pygame.K_d]:
        player_direction = 0
        if turns_allowed[0]:
            player_x += speed_player

    pygame.display.flip()
pygame.quit()
