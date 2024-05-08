# import thư viện
import socket
import threading
import json

# khai báo ip và port
host = '127.0.0.1'
port = 55555

# tạo socket và kết nối tới server trên host và port
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))


def packaging_data():
    json_data = json.dumps(
        {
            "nick_name": "View Data",
            "score": 0,
            "player_direction": 0,
            "player_x": 0,
            "player_y": 0
        }
    )
    # gửi dữ liệu lên server
    client.sendall(json_data.encode("ascii"))


# định nghĩa hàm nhận thông tin từ server
def receive():
    while True:
        try:
            # nhận dữ liệu từ server
            data = client.recv(1024).decode('ascii')
            print(data, "\n \n")
        except Exception as e:
            print(e)
            client.close()
            break


packaging_data()
# tạo thread nhận dữ liệu
receive_thread = threading.Thread(target=receive)
receive_thread.start()
