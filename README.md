# Pacman Game with Socket

## Giới thiệu

Đây là dự án tạo trò chơi Pacman sử dụng kết nối socket để cho phép nhiều người chơi cùng tham gia trò chơi. Trò chơi sẽ được viết bằng Python.

## Hướng dẫn cài đặt Python trên Linux

### Kiểm tra Python có sẵn hay không

Trên hầu hết các bản phân phối Linux, Python thường đi kèm sẵn. Bạn có thể kiểm tra phiên bản Python hiện tại bằng cách mở Terminal và chạy lệnh sau:

```bash
python3 --version
```
Nếu Python đã được cài đặt, bạn sẽ thấy phiên bản của nó xuất hiện. Nếu không, bạn sẽ nhận được một thông báo lỗi.

### Cài đặt Python
Nếu Python chưa được cài đặt trên hệ thống của bạn, bạn có thể sử dụng trình quản lý gói của bản phân phối Linux của mình để cài đặt Python.

Ví dụ với Ubuntu/Debian
Mở Terminal và chạy các lệnh sau:

```bash
sudo apt update
sudo apt install python3
```

Ví dụ với Fedora
Mở Terminal và chạy các lệnh sau:

```bash
sudo dnf install python3
```

Sau khi cài đặt hoàn tất, kiểm tra lại phiên bản Python để đảm bảo rằng nó đã được cài đặt thành công:
```bash
python3 --version
```

## Cài đặt Thư viện Pygame
Trong dự án của bạn, bạn sẽ cần cài đặt thư viện Pygame để phát triển trò chơi Pacman. Để cài đặt Pygame, bạn có thể sử dụng pip, trình quản lý gói cho Python.

```bash
pip install pygame
```

Sau khi cài đặt hoàn tất, bạn có thể kiểm tra xem Pygame đã được cài đặt thành công hay không bằng cách nhập:

```bash
python3 -m pygame.examples.aliens
```

Nếu Pygame đã được cài đặt đúng cách, bạn sẽ thấy một cửa sổ mới mở ra hiển thị một trò chơi mẫu.








