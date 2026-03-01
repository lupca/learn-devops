húng ta sẽ gộp **toàn bộ kiến thức của Ngày 1 và Ngày 2** vào một bài Lab thực chiến. Để có "sân chơi", 

Mục tiêu bài hôm nay: Tự tay tạo 2 con Server, cấu hình mạng cho chúng nhìn thấy nhau, set quyền file config chuẩn security, và thiết lập cho con Master tự động SSH chui vào con Slave mà không cần mật khẩu.

Vào việc!

---

### Bước 1: Khai sinh "Cụm Database" (Kiến thức mới: Multipass)


Tạo con Server thứ nhất (Master):

> `multipass launch 24.04 --name db-master --cpus 1 --memory 1G --disk 5G`

Tạo con Server thứ hai (Slave):

> `multipass launch 24.04 --name db-slave --cpus 1 --memory 1G --disk 5G`

Xem danh sách Server và **ghi lại IP** của cả 2 con (Cái này là IP mạng nội bộ - Ngày 2):

> `multipass list`

### Bước 2: Nối mạng & Phân tích Cổng (Ôn tập Ngày 2: Networking)

Mở 2 tab Terminal.

* **Tab 1:** Chui vào con Master bằng lệnh backdoor của Multipass: `multipass shell db-master`
* **Tab 2:** Chui vào con Slave: `multipass shell db-slave`

Trên con **db-master**, chị thử gọi sang con Slave xem mạng đã thông chưa (thay IP bằng IP của db-slave lấy ở Bước 1):

> `ping <IP_db_slave>`
> *(Nếu nó nhảy `time=...ms` liên tục là mạng đã thông lớp 3. Ấn Ctrl+C để dừng).*

Trên con **db-slave**, kiểm tra xem nó đang mở những port nào:

> `ss -tulpn`
> *(Chị sẽ thấy Port 22 - SSH đang mở trạng thái LISTEN. Nghĩa là nó sẵn sàng đón kết nối từ ngoài vào).*

### Bước 3: Thao tác File & Phân quyền (Ôn tập Ngày 1: Linux & Permissions)

Bây giờ chị quay lại Tab của con **db-master**. Chúng ta sẽ giả lập việc lưu một file chứa mật khẩu kết nối DB.

Tạo thư mục cấu hình và di chuyển vào đó:

> `mkdir -p /home/ubuntu/db_config`
> `cd /home/ubuntu/db_config`
> `pwd`

Tạo một file config chứa mật khẩu (lệnh này là in chữ và đẩy thẳng vào file):

> `echo "DB_PASSWORD=Sieumat@123" > .env`

Dùng lệnh `ls -la` để xem. Chị sẽ thấy file `.env` đang có quyền mặc định (thường là `664` hoặc `644`, tức là người khác - Others có thể đọc được). Đây là lỗ hổng chết người!

**Bài test cho chị:**

1. Hãy dùng lệnh `chmod` để set lại quyền cho file `.env` sao cho **chỉ duy nhất Owner (chủ file) được Đọc và Ghi**, còn Group và Others bị cấm tuyệt đối (Gợi ý: quyền `600`).
2. Set xong, thử đổi sang user khác (hoặc giả lập bằng cách gõ `chmod 000 .env` rồi gõ `cat .env` xem có bị lỗi *Permission denied* như Ngày 1 không, sau đó set lại `600`).
3. Dùng lệnh `grep` để lọc ra dòng chữ chứa "PASSWORD" trong file `.env` đó.

### Bước 4: Boss Fight - Giao tiếp không mật khẩu (Ôn tập Ngày 2: SSH Key)

Trong Database có cơ chế Replication (Master đẩy data sang Slave). Để làm được việc này, con `db-master` phải chui được vào `db-slave` liên tục mà không bị hỏi mật khẩu cản đường.

**Nhiệm vụ:** Mang "Ổ khóa" của db-master gắn sang db-slave.

**Trên db-master:**
Rèn cặp khóa mới tinh:

> `ssh-keygen -t ed25519 -C "master-to-slave"` *(Cứ Enter cho đến khi xong)*

In cái Public Key (Ổ khóa) ra màn hình và bôi đen Copy nó:

> `cat ~/.ssh/id_ed25519.pub`

**Sang Tab của db-slave:**
Tạo thư mục chứa khóa và set quyền cực kỳ nghiêm ngặt (nếu sai quyền, Linux sẽ từ chối khóa):

> `mkdir -p ~/.ssh`
> `chmod 700 ~/.ssh`

Mở file danh sách ổ khóa:

> `nano ~/.ssh/authorized_keys`

*Dán cái dòng chị vừa copy từ con master vào dòng cuối cùng của file này. Lưu lại (Ctrl+O -> Enter -> Ctrl+X).*

Set quyền cho file chứa khóa (Chỉ Owner được đọc/ghi):

> `chmod 600 ~/.ssh/authorized_keys`

**Nghiệm thu (Quay lại db-master):**
Từ con `db-master`, chị gõ lệnh SSH gọi thẳng sang IP của `db-slave`:

> `ssh ubuntu@<IP_db_slave>`

**BÙM!** Nếu dấu nhắc lệnh của chị tự động đổi từ `ubuntu@db-master` sang `ubuntu@db-slave` mà không hề hiện dòng chữ hỏi Password nào, xin chúc mừng! Chị đã hoàn thành xuất sắc việc kết hợp File Permissions, Networking và SSH Security. Gõ `exit` để thoát khỏi kết nối SSH.

### Bước 5: Thuật Hủy diệt - Dọn dẹp chiến trường

Thực hành xong rồi, đừng để rác trong máy. Thoát hết các tab Terminal (gõ `exit` về lại máy Laptop thật).

Xóa sạch 2 con Server đi (Giống lệnh `DROP DATABASE ... CASCADE`):

> `multipass delete db-master db-slave`
> `multipass purge`

Gõ lại `multipass list` chị sẽ thấy mọi thứ bốc hơi như chưa từng tồn tại.

---

Làm xong bài này, chị đã có tư duy cốt lõi nhất của một System Admin. Chị nghỉ ngơi đi.