import socket
import threading
import json
import pygame
import time

# khai báo ip và port
host = '127.0.0.1'
port = 55555

# tạo socket server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# khai báo mảng chứa danh sách clients
clients = []
nicknames = []
data_arr = []


# định nghĩa hàm gửi du lieu tới tất cả client
def send_data():
    while True:
        pygame.time.Clock().tick(120)
        try:
            if len(data_arr) > 0:
                for client in clients:
                    client.send(json.dumps(data_arr).encode("ascii"))
        except:
            pass


# đinh nghĩa hàm điều khiển client
def handle(client):
    if not send_thread.is_alive():
        send_thread.start()
    while True:
        pygame.time.Clock().tick(120)
        try:
            # nhận du lieu client
            data = client.recv(1024)
            data_json = json.loads(data.decode('ascii'))
            # gui lai du lieu
            if clients[0] == client:
                data_json["owner"] = "master"
                if len(data_arr) == 0:
                    data_arr.append(json.dumps(data_json))
                else:
                    data_arr[0] = json.dumps(data_json)
            else:
                index = clients.index(client)
                if len(data_arr) > index:
                    data_arr[index] = json.dumps(data_json)
                else:
                    data_arr.insert(index, json.dumps(data_json))
        except:
            # nếu lỗi thì remove client ra khỏi phòng
            index = clients.index(client)
            data_arr.pop(index)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            print(f"Remove {nickname} \n", len(clients))
            break


# định nghĩa hàm nhận kết nối từ client tới server
def receive():
    while True:
        client, address = server.accept()
        # thông báo kết nối của client từ address nào
        print(f'Connected with {str(address)}')
        # nhận tên nickname của client
        data = client.recv(1024)
        data_json = json.loads(data.decode('ascii'))
        # add nickname vào mảng nicknames để quản lý
        nickname = data_json["nick_name"]
        nicknames.append(nickname)
        # add client vào mảng client để quản lý
        clients.append(client)
        # in ra màn hình nickname đã join vào room
        print(f'Nickname of client is {nickname}')
        # tạo thread điều khiển client riêng biệt
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print('Server is listening...')
send_thread = threading.Thread(target=send_data)
# gọi hàm nhận thông tin
receive()


