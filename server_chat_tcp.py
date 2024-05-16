import socket
import sys
import threading
import json

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

running = True


def stop_server():
    while True:
        try:
            i = input("Enter 'exit' to close: \n")
            if i == "exit":
                raise
        except:
            close()
            break


def close():
    global running
    running = False
    print("--> Stopped running main.")
    server.close()
    print("--> Stopped socket.")
    sys.exit()


# định nghĩa hàm gửi message tới tất cả client trong room
def broadcast(message):
    for client in clients:
        client.send(message)


# đinh nghĩa hàm điều khiển client
def handle(client):
    thread_running = True
    while thread_running:
        try:
            # cho client gui nickname
            data = client.recv(1024)
            nickname = json.loads(data.decode())
            # nhận tên nickname của client
            if nickname in nicknames or len(nickname) == 0:
                client.send('NAME_ERROR'.encode())
            else:
                nicknames.append(nickname)
                # add client vào mảng client để quản lý
                clients.append(client)
                # gui thong bao cho client
                client.send('NAME_SUCCESS'.encode())
                # in ra màn hình nickname đã join vào room
                print(f'--> Nickname {nickname} join!')
                break
        except ConnectionResetError:
            thread_running = False

    while thread_running:
        try:
            # nhận message client
            data = client.recv(1024)
            # gọi broadcast message
            broadcast(data)
        except:
            # nếu lỗi thì remove client ra khỏi phòng
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            # broadcast thông báo client rời phòng
            broadcast(json.dumps(["LEFT_ROOM", nickname, "Left the room!"]).encode())
            print(f"--> {nickname} disconnect!")
            nicknames.remove(nickname)
            break


# định nghĩa hàm nhận kết nối từ client tới server
def receive():
    while running:
        try:
            client, address = server.accept()
            # thông báo kết nối của client từ address nào
            print(f'-> Connected with {str(address)}')
            # tao thread xu ly ket noi cho client
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        except:
            pass


print('Server is listening...')
thread_exit = threading.Thread(target=stop_server)
thread_exit.start()
# gọi hàm nhận thông tin
receive()

