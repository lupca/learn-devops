Hôm nay chúng ta sẽ học cách "mở cổng" và bảo vệ con Server đó khỏi hacker.

Trong Database, nếu để mật khẩu `admin/123456` và mở Port 5432 ra Internet, hacker sẽ dùng tool quét và bruteforce (đoán mật khẩu) sập server trong vòng 5 phút. Với máy chủ Linux cũng y hệt vậy.

Chị cài VMware/VirtualBox để thực hành nhé =))
---

## Ngày 2: Networking Cơ bản & baor mật bằng SSH Key

### 1. Ánh xạ khái niệm Mạng sang Database

Trước khi gõ lệnh, chị cần hiểu 3 thứ quyết định việc dữ liệu đi từ điểm A đến điểm B:

* **IP Address (Địa chỉ IP):** Giống như `Host` trong chuỗi kết nối Database. Nó định danh con Server đang nằm ở đâu. Có IP Public (ai trên Internet cũng gọi được) và IP Private (chỉ các máy trong cùng mạng nội bộ mới thấy nhau).
* **Port (Cổng kết nối):** Trên một IP có 65535 cái cổng. Dịch vụ nào chạy thì mở cổng đó. Ví dụ: PostgreSQL là `5432`, MySQL là `3306`, Web HTTP là `80`, và SSH (để điều khiển server) mặc định là `22`.
* **Subnet (Mạng con):** Tưởng tượng chị có 10 con DB. Chị gom chúng vào một "Khu vực cách ly" (VLAN/Subnet) chỉ cho phép chúng nói chuyện với nhau, cấm tiệt Internet can thiệp vào. Đó là Subnet.

### 2. SSH Key là gì? Tại sao Mật khẩu lại "Phế"?

Mật khẩu (Password) có một điểm yếu chết người: Nó có thể bị đoán ra bằng cách thử hàng triệu lần (Brute-force attack).

Để giải quyết, người ta dùng **SSH Key** (chữ ký mã hóa). Nó gồm 2 phần:

* **Public Key (Ổ khóa):** Chị đem cái ổ khóa này ném lên Server. Ai nhìn thấy cũng được, không sao cả.
* **Private Key (Chìa khóa):** Cái chìa này nằm chết trên laptop của chị, được mã hóa cực mạnh. Tuyệt đối không gửi cho ai.

Khi chị gõ lệnh đăng nhập, Server sẽ lấy "Ổ khóa" ra khớp với "Chìa khóa" trên máy chị. Khớp phát vào luôn, không cần gõ mật khẩu. Hacker có biết IP của chị cũng đứng khóc vì không có file Private Key.

---

### 3. Thực hành: Tự tay rèn "Chìa khóa" và Khóa chặt Server

Yêu cầu chị ấy mở Terminal trên máy cá nhân (Mac hoặc Linux/WSL trên Windows) và làm đúng thứ tự sau.

#### Bước 1: Rèn chìa khóa (Generate SSH Key)

Chị gõ lệnh này trên **máy cá nhân (Laptop)**, không phải trên máy ảo:

```bash
ssh-keygen -t ed25519 -C "db-admin-key"

```

*Giải thích lệnh:*

* `ssh-keygen`: Lệnh tạo khóa.
* `-t ed25519`: Thuật toán mã hóa (xịn và an toàn nhất hiện nay, thay cho RSA cũ).
* `-C`: Ghi chú để sau này nhìn vào biết khóa này của ai.

Hệ thống sẽ hỏi lưu ở đâu, cứ ấn **Enter** để mặc định. Nó hỏi có muốn tạo `passphrase` (mật khẩu bảo vệ cái chìa khóa) không, ấn **Enter** 2 lần bỏ qua cho nhanh (hoặc tự đặt tùy ý).

#### Bước 2: Kiểm tra cặp khóa vừa tạo

```bash
ls -la ~/.ssh

```

Chị sẽ thấy 2 file:

* `id_ed25519`: Đây là **Chìa khóa** (Private Key). Mất cái này là mất quyền vào Server. Lộ cái này là toang.
* `id_ed25519.pub`: Đây là **Ổ khóa** (Public Key). Chữ `.pub` nghĩa là Public.

Thử xem mặt mũi cái "Ổ khóa" nó ra sao:

```bash
cat ~/.ssh/id_ed25519.pub

```

Chị sẽ thấy một chuỗi ký tự loằng ngoằng. Copy toàn bộ chuỗi đó lại.

#### Bước 3: Đem "Ổ khóa" gắn lên Server (Cài đặt Public Key)

Bây giờ, chị đăng nhập vào con Server (hoặc máy ảo) bằng mật khẩu như bình thường một lần cuối cùng.
Vào được Server rồi, gõ các lệnh sau để tạo chỗ cất "Ổ khóa":

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys

```

*Giải thích:* Tạo thư mục `.ssh`, cấp quyền `700` (chỉ mình chủ nhân được vào, y như bài học hôm trước). Mở file `authorized_keys` lên bằng trình soạn thảo Nano.

**Dán cái chuỗi Public Key** chị vừa copy ở Bước 2 vào file này. Xong ấn `Ctrl + O` -> `Enter` để lưu, `Ctrl + X` để thoát Nano.

Chốt quyền cho file khóa (Rất quan trọng, sai quyền là Linux từ chối nhận khóa):

```bash
chmod 600 ~/.ssh/authorized_keys

```

#### Bước 4: Chặn đường lui - Cấm đăng nhập bằng mật khẩu

Đây là thao tác chuẩn của DevSecOps. Đã dùng chìa khóa thì vứt luôn ổ cắm mật khẩu đi.

Trên con Server, gõ:

```bash
sudo nano /etc/ssh/sshd_config

```

Chị dùng phím mũi tên kéo xuống, tìm dòng có chữ `PasswordAuthentication yes` (hoặc đang bị # ở đầu). Sửa lại thành:
`PasswordAuthentication no`

Lưu lại (Ctrl+O -> Enter -> Ctrl+X) và khởi động lại dịch vụ SSH để áp dụng luật mới:

```bash
sudo systemctl restart sshd

```

#### Bước 5: Tận hưởng thành quả

Bây giờ chị gõ `exit` để thoát khỏi Server, trở về màn hình máy Laptop.
Gõ lệnh đăng nhập lại:

```bash
ssh user_cua_chi@IP_cua_server

```

**Bùm!** Chị sẽ vào thẳng Server trong một nốt nhạc mà không bị hỏi mật khẩu nữa.

---

**Câu hỏi kiểm tra tư duy cuối ngày:**
Nếu ngày mai laptop của chị bị hỏng ổ cứng, chị mất file Private Key (`id_ed25519`), trong khi Server thì đã khóa chức năng đăng nhập bằng Password rồi. Chị sẽ làm thế nào để vào lại được con Server đó? (Gợi ý: Suy nghĩ về cơ chế dự phòng Break-glass trong hệ thống quản trị).
