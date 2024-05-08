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
nick_name = "Nguyen Van A"

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


# ramdom food
def random_to_number(matrix, num_to_replace=10, replace_to=1):
    n = len(matrix)  # Số hàng của ma trận
    m = len(matrix[0])  # Số cột của ma trận

    # Tìm và chọn ngẫu nhiên các vị trí 0 để thay thế
    replace_indices = []
    for _ in range(num_to_replace):
        while True:
            i = random.randint(0, n - 1)  # Chọn một chỉ số hàng ngẫu nhiên
            j = random.randint(0, m - 1)  # Chọn một chỉ số cột ngẫu nhiên
            if matrix[i][j] == 0:  # Nếu giá trị tại vị trí này là 0, thì thêm vào danh sách và thoát vòng lặp
                replace_indices.append((i, j))
                break

    # Thay thế các số 0 tại các vị trí đã chọn thành 1
    for i, j in replace_indices:
        matrix[i][j] = replace_to

    return matrix


# thông tin map
map_level = copy.deepcopy(map_level_1)
# số lượng thức ăn nhỏ
map_level = random_to_number(map_level, 70)
# số lượng thức ăn lớn
map_level = random_to_number(map_level, 3, 2)

# thông tin fps
timer = pygame.time.Clock()
fps = 60

# tải phông chữ
font_path = "font/Roboto/Roboto-Regular.ttf"
font = pygame.font.Font(font_path, 20)

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

# cài đặt thông tin thức ăn nhấp nháy
flicker_food = False
loop_count_flicker_food = 0
flick_food_after_loop = 50
un_visible_food_loop = 10


# random pacman ra vị trí còn trống ngẫu nhiên
def random_empty_position(matrix):
    empty_positions = [(y, x) for y in range(len(matrix) - 1) for x in range(len(matrix[0]) - 1) if matrix[y][x] == 0]
    if empty_positions:
        return random.choice(empty_positions)
    else:
        return None


# thông tin của pacman
player_y, player_x = random_empty_position(map_level)
player_x = player_x * 25
player_y = player_y * 25
center_player_x = 0
center_player_y = 0
player_direction = 0
loop_count_player = 0
speed_player = 2
turns_allowed = [False, False, False, False]  # Right, Left, Up, Down
total_score = 0
flicker_player = False
count_flicker_player = 0
player_flicker_time_default = 200
player_flicker_time_count = player_flicker_time_default

# thông tin mấy con ma
ghost_is_slow = False
ghost_slow_time_count = 0
ghost_slow_time_default = 600

red_ghost_y, red_ghost_x = random_empty_position(map_level)
red_ghost_x = red_ghost_x * 25
red_ghost_y = red_ghost_y * 25
red_ghost_direction = 0
red_ghost_dead = False
red_dead_time_count = 0
red_dead_time_default = 400
flicker_red_ghost_clock = 0

blue_ghost_y, blue_ghost_x = random_empty_position(map_level)
blue_ghost_x = blue_ghost_x * 25
blue_ghost_y = blue_ghost_y * 25
blue_ghost_direction = 1
blue_ghost_dead = False
blue_dead_time_count = 0
blue_dead_time_default = 400
flicker_blue_ghost_clock = 0

orange_ghost_y, orange_ghost_x = random_empty_position(map_level)
orange_ghost_x = orange_ghost_x * 25
orange_ghost_y = orange_ghost_y * 25
orange_ghost_direction = 2
orange_ghost_dead = False
orange_dead_time_count = 0
orange_dead_time_default = 400
flicker_orange_ghost_clock = 0

pink_ghost_y, pink_ghost_x = random_empty_position(map_level)
pink_ghost_x = pink_ghost_x * 25
pink_ghost_y = pink_ghost_y * 25
pink_ghost_direction = 3
pink_ghost_dead = False
pink_dead_time_count = 0
pink_dead_time_default = 400
flicker_pink_ghost_clock = 0

ghost_speeds_default = [3, 2, 2, 2]
ghost_speeds = ghost_speeds_default


def random_player_position(matrix):
    y, x = random_empty_position(matrix)
    return x * 25, y * 25


def draw_board():
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


def draw_player():
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    if player_direction == 0:
        screen.blit(player_images[loop_count_player // 5], (player_x, player_y))
    elif player_direction == 1:
        screen.blit(pygame.transform.flip(player_images[loop_count_player // 5], True, False), (player_x, player_y))
    elif player_direction == 2:
        screen.blit(pygame.transform.rotate(player_images[loop_count_player // 5], 90), (player_x, player_y))
    elif player_direction == 3:
        screen.blit(pygame.transform.rotate(player_images[loop_count_player // 5], 270), (player_x, player_y))


def draw_flicker_player():
    global count_flicker_player
    if count_flicker_player < 10:
        count_flicker_player += 1
    elif count_flicker_player < 20:
        count_flicker_player += 1
        # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
        if player_direction == 0:
            screen.blit(player_images[loop_count_player // 5], (player_x, player_y))
        elif player_direction == 1:
            screen.blit(pygame.transform.flip(player_images[loop_count_player // 5], True, False), (player_x, player_y))
        elif player_direction == 2:
            screen.blit(pygame.transform.rotate(player_images[loop_count_player // 5], 90), (player_x, player_y))
        elif player_direction == 3:
            screen.blit(pygame.transform.rotate(player_images[loop_count_player // 5], 270), (player_x, player_y))
    else:
        count_flicker_player = 0


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


def check_eat_food(score):
    global ghost_is_slow
    global ghost_speeds
    global ghost_slow_time_count
    height_a_rec = HEIGHT_PLAYING // len(map_level)
    width_a_rec = WIDTH_PLAYING // len(map_level[0])
    if map_level[center_player_y // height_a_rec][center_player_x // width_a_rec] == 1:
        map_level[center_player_y // height_a_rec][center_player_x // width_a_rec] = 0
        score += 10
    if map_level[center_player_y // height_a_rec][center_player_x // width_a_rec] == 2:
        map_level[center_player_y // height_a_rec][center_player_x // width_a_rec] = 0
        score += 50
        ghost_is_slow = True
        ghost_speeds = [1, 1, 1, 1]
        ghost_slow_time_count += ghost_slow_time_default
    return score


def check_collisions_ghost(player_location_x, player_location_y, ghost_x, ghost_y):
    if (ghost_x < player_location_x + 25 < ghost_x + 25 and ghost_y < player_location_y + 25 < ghost_y + 25) \
            or (ghost_x <= player_location_x < ghost_x + 25 and ghost_y <= player_location_y < ghost_y + 25) \
            or (ghost_x < player_location_x + 25 < ghost_x + 25 and ghost_y < player_location_y < ghost_y + 25) \
            or (ghost_x <= player_location_x < ghost_x + 25 and ghost_y <= player_location_y + 25 < ghost_y + 25):
        return True
    else:
        return False


def player_dead(matrix):
    global flicker_player
    x, y = random_player_position(matrix)
    flicker_player = True
    return x, y


def draw_message(list_message=0):
    pygame.draw.rect(screen, (55, 0, 0), (WIDTH_PLAYING, HEIGHT_SCORE_TABLE, WIDTH_BOX_CHAT, HEIGHT_BOX_CHAT))


def draw_score(list_score=0):
    pygame.draw.rect(screen, (255, 0, 0), (WIDTH_PLAYING, 0, WIDTH_SCORE_TABLE, HEIGHT_SCORE_TABLE))


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

    def check_position(self):
        if map_level[self.y_pos // 25][(self.x_pos - self.speed) // 25] < 3:
            self.turns[1] = True
        if map_level[self.y_pos // 25][(self.x_pos + 25) // 25] < 3:
            self.turns[0] = True
        if map_level[(self.y_pos + 25) // 25][self.x_pos // 25] < 3:
            self.turns[3] = True
        if map_level[(self.y_pos - self.speed) // 25][self.x_pos // 25] < 3:
            self.turns[2] = True

    @staticmethod
    def random_direction(list_direction):
        return random.choice(list_direction)

    def move(self):
        # r, l, u, d
        self.check_position()

        if self.x_pos > WIDTH_PLAYING - 30:
            self.x_pos = 15
        if self.x_pos < 15:
            self.x_pos = WIDTH_PLAYING - 30
        if self.y_pos > HEIGHT_PLAYING - 30:
            self.y_pos = 15
        if self.y_pos < 15:
            self.y_pos = HEIGHT_PLAYING - 30

        if self.direction == 0:
            if self.turns[0]:
                self.x_pos += self.speed
            else:
                self.direction = self.random_direction([1, 2, 3])
        elif self.direction == 1:
            if self.turns[1]:
                self.x_pos -= self.speed
            else:
                self.direction = self.random_direction([0, 2, 3])
        elif self.direction == 2:
            if self.turns[2]:
                self.y_pos -= self.speed
            else:
                self.direction = self.random_direction([0, 1, 3])
        elif self.direction == 3:
            if self.turns[3]:
                self.y_pos += self.speed
            else:
                self.direction = self.random_direction([0, 1, 2])
        return self.x_pos, self.y_pos, self.direction


game_running = True


def receive_data():
    global red_ghost_x, red_ghost_y, red_ghost_direction, red_ghost_dead, red_dead_time_count, red_dead_time_default,\
        flicker_red_ghost_clock, blue_ghost_x, blue_ghost_y, blue_ghost_direction, blue_ghost_dead, \
        blue_dead_time_count, blue_dead_time_default, flicker_blue_ghost_clock, orange_ghost_x, orange_ghost_y,\
        orange_ghost_direction, orange_ghost_dead, orange_dead_time_count, orange_dead_time_default,\
        flicker_orange_ghost_clock, pink_ghost_x, pink_ghost_y, pink_ghost_direction, pink_ghost_dead,\
        pink_dead_time_count, pink_dead_time_default, flicker_pink_ghost_clock
    while True:
        timer.tick(fps * 2)
        try:
            # Nhận phản hồi từ server
            response, server_address = client_socket.recvfrom(4096)
            data = json.loads(response.decode())
            data_ghost = data["ghost"]
            red_ghost_x = data_ghost[0]
            red_ghost_y = data_ghost[1]
            red_ghost_direction = data_ghost[2]
            red_ghost_dead = data_ghost[3]
            red_dead_time_count = data_ghost[4]
            red_dead_time_default = data_ghost[5]
            flicker_red_ghost_clock = data_ghost[6]

            blue_ghost_x = data_ghost[7]
            blue_ghost_y = data_ghost[8]
            blue_ghost_direction = data_ghost[9]
            blue_ghost_dead = data_ghost[10]
            blue_dead_time_count = data_ghost[11]
            blue_dead_time_default = data_ghost[12]
            flicker_blue_ghost_clock = data_ghost[13]

            orange_ghost_x = data_ghost[14]
            orange_ghost_y = data_ghost[15]
            orange_ghost_direction = data_ghost[16]
            orange_ghost_dead = data_ghost[17]
            orange_dead_time_count = data_ghost[18]
            orange_dead_time_default = data_ghost[19]
            flicker_orange_ghost_clock = data_ghost[20]

            pink_ghost_x = data_ghost[21]
            pink_ghost_y = data_ghost[22]
            pink_ghost_direction = data_ghost[23]
            pink_ghost_dead = data_ghost[24]
            pink_dead_time_count = data_ghost[25]
            pink_dead_time_default = data_ghost[26]
            flicker_pink_ghost_clock = data_ghost[27]
        except Exception as e:
            print(e)


def send_data():
    json_data = json.dumps(
        [nick_name, total_score, player_direction, player_x, player_y]
    )
    # gửi dữ liệu lên server
    client_socket.sendto(json_data.encode(), server_address)


receive_thread = threading.Thread(target=receive_data)
receive_thread.start()

while game_running:
    # đặt fps
    timer.tick(fps)

    send_data()

    # va chạm với ma
    collisions_red = check_collisions_ghost(player_x, player_y, red_ghost_x, red_ghost_y)
    if collisions_red:
        if ghost_is_slow and not red_ghost_dead:
            red_ghost_y = len(map_level) // 2 * 25
            red_ghost_x = len(map_level[0]) // 2 * 25
            red_ghost_dead = True
        else:
            player_x, player_y = player_dead(map_level)
    collisions_blue = check_collisions_ghost(player_x, player_y, blue_ghost_x, blue_ghost_y)
    if collisions_blue:
        if ghost_is_slow and not blue_ghost_dead:
            blue_ghost_y = (len(map_level) - 1) // 2 * 25
            blue_ghost_x = len(map_level[0]) // 2 * 25
            blue_ghost_dead = True
        else:
            player_x, player_y = player_dead(map_level)
    collisions_pink = check_collisions_ghost(player_x, player_y, pink_ghost_x, pink_ghost_y)
    if collisions_pink:
        if ghost_is_slow and not pink_ghost_dead:
            pink_ghost_y = (len(map_level) - 2) // 2 * 25
            pink_ghost_x = (len(map_level[0]) - 1) // 2 * 25
            pink_ghost_dead = True
        else:
            player_x, player_y = player_dead(map_level)
    collisions_orange = check_collisions_ghost(player_x, player_y, orange_ghost_x, orange_ghost_y)
    if collisions_orange:
        if ghost_is_slow and not orange_ghost_dead:
            orange_ghost_y = len(map_level) // 2 * 25
            orange_ghost_x = (len(map_level[0]) - 1) // 2 * 25
            orange_ghost_dead = True
        else:
            player_x, player_y = player_dead(map_level)

    # thời gian ma hẹo
    if red_ghost_dead and red_dead_time_count > 0:
        red_dead_time_count -= 1
    else:
        red_ghost_dead = False
        red_dead_time_count = red_dead_time_default
    if blue_ghost_dead and blue_dead_time_count > 0:
        blue_dead_time_count -= 1
    else:
        blue_ghost_dead = False
        blue_dead_time_count = blue_dead_time_default
    if pink_ghost_dead and pink_dead_time_count > 0:
        pink_dead_time_count -= 1
    else:
        pink_ghost_dead = False
        pink_dead_time_count = pink_dead_time_default
    if orange_ghost_dead and orange_dead_time_count > 0:
        orange_dead_time_count -= 1
    else:
        orange_ghost_dead = False
        orange_dead_time_count = orange_dead_time_default

    # nhấp nháy thức ăn lớn
    if loop_count_flicker_food < flick_food_after_loop:
        loop_count_flicker_food += 1
        # thời gian ẩn
        if loop_count_flicker_food > un_visible_food_loop:
            flicker_food = False
    else:
        loop_count_flicker_food = 0
        flicker_food = True

    # cơ hàm pacman
    if loop_count_player < 19:
        loop_count_player += 1
    else:
        loop_count_player = 0

    # thời gian slow mấy con ma
    if ghost_is_slow and ghost_slow_time_count > 0:
        ghost_slow_time_count -= 1
    else:
        ghost_is_slow = False
        ghost_slow_time_count = 0
        ghost_speeds = ghost_speeds_default

    # thời gian nhấp nháy của pacman
    if flicker_player and player_flicker_time_count > 0:
        player_flicker_time_count -= 1
    else:
        flicker_player = False
        player_flicker_time_count = player_flicker_time_default

    # đặt màu nền
    screen.fill(background_color)

    # lấy điểm giữa của pacman
    center_player_x = player_x + 12
    center_player_y = player_y + 13

    # Hướng được phép di chuyển
    turns_allowed = check_position(player_x, player_y)

    #  Đi qua cổng nối
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
    draw_board()

    # pacman
    if flicker_player:
        draw_flicker_player()
    else:
        draw_player()

    # ma đỏ
    red_ghost = Ghost(red_ghost_x, red_ghost_y, ghost_speeds[0], red_ghost_image, red_ghost_direction, red_ghost_dead)
    flicker_red_ghost_clock = red_ghost.draw(flicker_red_ghost_clock)
    # if not red_ghost_dead:
    #     red_ghost_x, red_ghost_y, red_ghost_direction = red_ghost.move()

    # ma xanh
    blue_ghost = Ghost(blue_ghost_x, blue_ghost_y, ghost_speeds[1], blue_ghost_image, blue_ghost_direction,
                       blue_ghost_dead)
    flicker_blue_ghost_clock = blue_ghost.draw(flicker_blue_ghost_clock)
    # if not blue_ghost_dead:
    #     blue_ghost_x, blue_ghost_y, blue_ghost_direction = blue_ghost.move()

    # ma hồng
    pink_ghost = Ghost(pink_ghost_x, pink_ghost_y, ghost_speeds[2], pink_ghost_image, pink_ghost_direction,
                       pink_ghost_dead)
    flicker_pink_ghost_clock = pink_ghost.draw(flicker_pink_ghost_clock)
    # if not pink_ghost_dead:
    #     pink_ghost_x, pink_ghost_y, pink_ghost_direction = pink_ghost.move()

    # ma cam
    orange_ghost = Ghost(orange_ghost_x, orange_ghost_y, ghost_speeds[3], orange_ghost_image, orange_ghost_direction,
                         orange_ghost_dead)
    flicker_orange_ghost_clock = orange_ghost.draw(flicker_orange_ghost_clock)
    # if not orange_ghost_dead:
    #     orange_ghost_x, orange_ghost_y, orange_ghost_direction = orange_ghost.move()

    # score
    total_score = check_eat_food(total_score)
    draw_score()

    # tin nhắn
    draw_message()

    # sự kiện điều khiển
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False

    key_pressed = pygame.key.get_pressed()
    # Di chuyển người chơi
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
