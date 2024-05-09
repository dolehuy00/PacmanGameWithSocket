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
data_clients = {}

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

red_ghost_x, red_ghost_y = random_empty_position(map_level)
red_ghost_direction = 0
red_ghost_dead = False
red_dead_time_count = 0
red_dead_time_default = 400

blue_ghost_x, blue_ghost_y = random_empty_position(map_level)
blue_ghost_direction = 1
blue_ghost_dead = False
blue_dead_time_count = 0
blue_dead_time_default = 400

orange_ghost_x, orange_ghost_y = random_empty_position(map_level)
orange_ghost_direction = 2
orange_ghost_dead = False
orange_dead_time_count = 0
orange_dead_time_default = 400

pink_ghost_x, pink_ghost_y = random_empty_position(map_level)
pink_ghost_direction = 3
pink_ghost_dead = False
pink_dead_time_count = 0
pink_dead_time_default = 400

ghost_speeds_default = [3, 2, 2, 2]
ghost_speeds = ghost_speeds_default


# lớp ma
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


# hàm kiểm tra va chạm với 1 ma
def check_collision_ghost(player_location_x, player_location_y, ghost_x, ghost_y):
    if (ghost_x < player_location_x + 25 < ghost_x + 25 and ghost_y < player_location_y + 25 < ghost_y + 25) \
            or (ghost_x <= player_location_x < ghost_x + 25 and ghost_y <= player_location_y < ghost_y + 25) \
            or (ghost_x < player_location_x + 25 < ghost_x + 25 and ghost_y < player_location_y < ghost_y + 25) \
            or (ghost_x <= player_location_x < ghost_x + 25 and ghost_y <= player_location_y + 25 < ghost_y + 25):
        return True
    else:
        return False


# hàm cho ma di chuyển
def run_ghost():
    global red_ghost_x, red_ghost_y, red_ghost_direction, blue_ghost_x, blue_ghost_y, blue_ghost_direction, \
        pink_ghost_x, pink_ghost_y, pink_ghost_direction, orange_ghost_x, orange_ghost_y, orange_ghost_direction, \
        red_ghost_dead, red_dead_time_count, blue_ghost_dead, blue_dead_time_count, pink_ghost_dead, \
        pink_dead_time_count, orange_ghost_dead, orange_dead_time_count, ghost_is_slow, ghost_slow_time_count, \
        ghost_speeds
    while True:
        clock.tick(fps)

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

        # thời gian slow mấy con ma
        if ghost_is_slow and ghost_slow_time_count > 0:
            ghost_slow_time_count -= 1
        else:
            ghost_is_slow = False
            ghost_slow_time_count = 0
            ghost_speeds = ghost_speeds_default

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


# hàm đóng gói dữ liệu ma
def build_data_ghost():
    return [
            red_ghost_x, red_ghost_y, red_ghost_direction, red_ghost_dead, red_dead_time_count,
            red_dead_time_default, blue_ghost_x, blue_ghost_y, blue_ghost_direction, blue_ghost_dead,
            blue_dead_time_count, blue_dead_time_default, orange_ghost_x, orange_ghost_y, orange_ghost_direction,
            orange_ghost_dead, orange_dead_time_count, orange_dead_time_default, pink_ghost_x, pink_ghost_y,
            pink_ghost_direction, pink_ghost_dead, pink_dead_time_count, pink_dead_time_default, ghost_speeds,
            ghost_is_slow
    ]


# hàm kiểm tra va chạm với các con ma
def check_player_collisions_ghosts(player_location_x, player_location_y):
    global red_ghost_x, red_ghost_y, blue_ghost_x, blue_ghost_y, pink_ghost_x, pink_ghost_y, orange_ghost_x,\
        orange_ghost_y, red_ghost_dead, blue_ghost_dead, pink_ghost_dead, orange_ghost_dead
    player_dead = True
    # va chạm với ma
    collisions_red = check_collision_ghost(player_location_x, player_location_y, red_ghost_x, red_ghost_y)
    if collisions_red:
        if ghost_is_slow and not red_ghost_dead:
            red_ghost_y = len(map_level) // 2 * 25
            red_ghost_x = len(map_level[0]) // 2 * 25
            red_ghost_dead = True
        else:
            return player_dead
    collisions_blue = check_collision_ghost(player_location_x, player_location_y, blue_ghost_x, blue_ghost_y)
    if collisions_blue:
        if ghost_is_slow and not blue_ghost_dead:
            blue_ghost_y = (len(map_level) - 1) // 2 * 25
            blue_ghost_x = len(map_level[0]) // 2 * 25
            blue_ghost_dead = True
        else:
            return player_dead
    collisions_pink = check_collision_ghost(player_location_x, player_location_y, pink_ghost_x, pink_ghost_y)
    if collisions_pink:
        if ghost_is_slow and not pink_ghost_dead:
            pink_ghost_y = (len(map_level) - 2) // 2 * 25
            pink_ghost_x = (len(map_level[0]) - 1) // 2 * 25
            pink_ghost_dead = True
        else:
            return player_dead
    collisions_orange = check_collision_ghost(player_location_x, player_location_y, orange_ghost_x, orange_ghost_y)
    if collisions_orange:
        if ghost_is_slow and not orange_ghost_dead:
            orange_ghost_y = len(map_level) // 2 * 25
            orange_ghost_x = (len(map_level[0]) - 1) // 2 * 25
            orange_ghost_dead = True
        else:
            return player_dead

    return False


# hàm kiểm tra ăn thức ăn
def check_eat_food(player_location_x, player_location_y):
    global ghost_is_slow
    global ghost_speeds
    global ghost_slow_time_count
    total_new_score = 0
    eaten_food = False
    # lấy điểm giữa của pacman
    center_player_x = player_location_x + 12
    center_player_y = player_location_y + 13
    # lấy kích thước 1 ô
    height_a_rec = HEIGHT_PLAYING // len(map_level)
    width_a_rec = WIDTH_PLAYING // len(map_level[0])
    if map_level[center_player_y // height_a_rec][center_player_x // width_a_rec] == 1:
        map_level[center_player_y // height_a_rec][center_player_x // width_a_rec] = 0
        total_new_score += 100
        eaten_food = True
    if map_level[center_player_y // height_a_rec][center_player_x // width_a_rec] == 2:
        map_level[center_player_y // height_a_rec][center_player_x // width_a_rec] = 0
        total_new_score += 500
        eaten_food = True
        ghost_is_slow = True
        ghost_speeds = [1, 1, 1, 1]
        ghost_slow_time_count += ghost_slow_time_default
    return eaten_food, total_new_score


# hàm gửi dữ liệu map, ghost, other player cho các client khác
def send_data():
    try:
        for client in connected_clients:
            data_send = {}
            data_other_player = data_clients.copy()
            data_other_player.pop(str(client))
            data_send["ghost"] = build_data_ghost()
            data_send["map"] = map_level
            data_send["otherPlayer"] = list(data_other_player.values())
            if len(data_send) > 0:
                server_socket.sendto(json.dumps(data_send).encode(), client)
    except:
        pass


# hàm gửi data cho client gửi request
def send_you_data(data_send, client):
    server_socket.sendto(json.dumps(data_send).encode(), client)


def handel_score_player():
    while True:
        pygame.time.Clock().tick(2)
        if len(data_clients) > 0:
            data_score_players = {}
            for client_data in list(data_clients.values()):
                data_score_players[client_data[0]] = client_data[6]
            try:
                sorted_score_table = dict(sorted(data_score_players.items(), key=lambda item: item[1], reverse=True))
                for client in connected_clients:
                    server_socket.sendto(json.dumps({"score_table": sorted_score_table}).encode(), client)
            except:
                pass


# chạy luồng cho ma di chuyển
run_ghost_thread = threading.Thread(target=run_ghost)
run_ghost_thread.start()

# luoofng guwwi bang xep hangj
thread_send_data_to_all_client = threading.Thread(target=handel_score_player)
thread_send_data_to_all_client.start()

# nhận request từ client
while True:
    try:
        # Nhận dữ liệu từ client
        data, client_address = server_socket.recvfrom(4096)

        # xử lý dữ liệu nhận được
        connected_clients.add(client_address)
        data_json = json.loads(data.decode())
        player_x = data_json[1]
        player_y = data_json[2]
        # check flicker
        if not data_json[5]:
            # check player dead
            player_is_dead = check_player_collisions_ghosts(player_x, player_y)
            if player_is_dead:
                data_json[4] = player_is_dead
                # random player
                player_x, player_y = random_empty_position(map_level)
                data_json[1] = player_x
                data_json[2] = player_y
                # gửi lại dữ liệu cho các client
                thread_send_data_to_client = threading.Thread(target=send_you_data, args=({"you": data_json}, client_address,))
                thread_send_data_to_client.start()
        # check eat food
        is_eaten, score = check_eat_food(player_x, player_y)
        if is_eaten:
            data_json[6] += score
            thread_send_data_to_client = threading.Thread(target=send_you_data, args=({"you": data_json}, client_address,))
            thread_send_data_to_client.start()
        # thêm dữ liệu vào gói
        data_clients.update({str(client_address): data_json})

        # gửi lại dữ liệu cho các client
        thread_send_data_to_other_client = threading.Thread(target=send_data)
        thread_send_data_to_other_client.start()

    except ConnectionResetError as e:
        # Xử lý khi một client ngắt kết nối
        connected_clients.clear()
        data_clients.clear()
        print("Client", client_address, "đã ngắt kết nối.")
        print(e)
