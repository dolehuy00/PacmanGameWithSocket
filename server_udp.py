import socket
import json
import pygame
import threading
from map import map_level_1
import copy
import random

# Tạo socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 12345)
server_socket.bind(server_address)

# Danh sách các client đang kết nối
connected_clients = set()
data_arr = {}

# đặt kích thước các màn hình
WIDTH_PLAYING = 900
HEIGHT_PLAYING = 750


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


# random pacman ra vị trí còn trống ngẫu nhiên
def random_empty_position(matrix):
    empty_positions = [(y, x) for y in range(len(matrix) - 1) for x in range(len(matrix[0]) - 1) if matrix[y][x] == 0]
    if empty_positions:
        return random.choice(empty_positions)
    else:
        return None


# thông tin fps
clock = pygame.time.Clock()
fps = 60


# thông tin map
map_level = copy.deepcopy(map_level_1)
# số lượng thức ăn nhỏ
map_level = random_to_number(map_level, 70)
# số lượng thức ăn lớn
map_level = random_to_number(map_level, 3, 2)

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


class Ghost:
    def __init__(self, x_pos, y_pos, speed, direct, dead):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.center_x = self.x_pos + 12
        self.center_y = self.y_pos + 12
        self.speed = speed
        self.direction = direct
        self.dead = dead
        self.id = id
        self.turns = [False, False, False, False]  # Right, Left, Up, Down

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


def check_collisions_ghost(player_location_x, player_location_y, ghost_x, ghost_y):
    if (ghost_x < player_location_x + 25 < ghost_x + 25 and ghost_y < player_location_y + 25 < ghost_y + 25) \
            or (ghost_x <= player_location_x < ghost_x + 25 and ghost_y <= player_location_y < ghost_y + 25) \
            or (ghost_x < player_location_x + 25 < ghost_x + 25 and ghost_y < player_location_y < ghost_y + 25) \
            or (ghost_x <= player_location_x < ghost_x + 25 and ghost_y <= player_location_y + 25 < ghost_y + 25):
        return True
    else:
        return False


def run_ghost():
    global red_ghost_x, red_ghost_y, red_ghost_direction, blue_ghost_x, blue_ghost_y, blue_ghost_direction, \
        pink_ghost_x, pink_ghost_y, pink_ghost_direction, orange_ghost_x, orange_ghost_y, orange_ghost_direction
    while True:
        clock.tick(fps)
        # ma đỏ
        red_ghost = Ghost(red_ghost_x, red_ghost_y, ghost_speeds[0], red_ghost_direction, red_ghost_dead)
        if not red_ghost_dead:
            red_ghost_x, red_ghost_y, red_ghost_direction = red_ghost.move()

        # ma xanh
        blue_ghost = Ghost(blue_ghost_x, blue_ghost_y, ghost_speeds[1], blue_ghost_direction,
                           blue_ghost_dead)
        if not blue_ghost_dead:
            blue_ghost_x, blue_ghost_y, blue_ghost_direction = blue_ghost.move()

        # ma hồng
        pink_ghost = Ghost(pink_ghost_x, pink_ghost_y, ghost_speeds[2], pink_ghost_direction,
                           pink_ghost_dead)
        if not pink_ghost_dead:
            pink_ghost_x, pink_ghost_y, pink_ghost_direction = pink_ghost.move()

        # ma cam
        orange_ghost = Ghost(orange_ghost_x, orange_ghost_y, ghost_speeds[3], orange_ghost_direction,
                             orange_ghost_dead)
        if not orange_ghost_dead:
            orange_ghost_x, orange_ghost_y, orange_ghost_direction = orange_ghost.move()


def build_data_ghost():
    return [
            red_ghost_x, red_ghost_y, red_ghost_direction, red_ghost_dead, red_dead_time_count, red_dead_time_default,
            flicker_red_ghost_clock, blue_ghost_x, blue_ghost_y, blue_ghost_direction, blue_ghost_dead,
            blue_dead_time_count, blue_dead_time_default, flicker_blue_ghost_clock, orange_ghost_x, orange_ghost_y,
            orange_ghost_direction, orange_ghost_dead, orange_dead_time_count, orange_dead_time_default,
            flicker_orange_ghost_clock, pink_ghost_x, pink_ghost_y, pink_ghost_direction, pink_ghost_dead,
            pink_dead_time_count, pink_dead_time_default, flicker_pink_ghost_clock, ghost_speeds
    ]


def send_data():
    try:
        for client in connected_clients:
            data_send = data_arr.copy()
            data_send.pop(str(client))
            data_send["ghost"] = build_data_ghost()
            data_send["map"] = map_level
            if len(data_send) > 0:
                server_socket.sendto(json.dumps(data_send).encode(), client)
    except:
        pass


run_ghost_thread = threading.Thread(target=run_ghost)
run_ghost_thread.start()

while True:
    clock.tick(fps * 2)
    try:
        # Nhận dữ liệu từ client
        data, client_address = server_socket.recvfrom(4096)

        # xử lý dữ liệu nhận được
        connected_clients.add(client_address)
        data_arr.update({str(client_address): json.loads(data.decode())})

        # gửi lại dữ liệu cho các client
        thread = threading.Thread(target=send_data)
        thread.start()

    except ConnectionResetError as e:
        # Xử lý khi một client ngắt kết nối
        connected_clients.clear()
        data_arr.clear()
        print("Client", client_address, "đã ngắt kết nối.")
