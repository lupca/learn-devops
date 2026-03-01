Chào chị! Mấy ngày qua gõ tay từng lệnh là để hiểu bản chất. Nhưng trong thực tế dự án, gõ đi gõ lại mớ lệnh đó thì hệ thống có ngày "sập" vì lỗi đánh máy (human error).

Một kỹ sư thực thụ sẽ gom tất cả các lệnh đó vào một file kịch bản và chạy nó bằng một cú Enter. Trong Database, chị gọi nó là **Stored Procedure** hay **PL/pgSQL**. Ở thế giới Linux và DevSecOps, nó gọi là **Bash Script**.

Dưới đây là một dự án thực tế: **"One-Click DB Provisioning"**. Chị sẽ viết một kịch bản tự động hóa hoàn toàn Ngày 1, Ngày 2 và Ngày 3: Tự đẻ Server, tự móc IP ra, tự rèn khóa SSH và tự động đẩy khóa vào Server để bảo mật.

---

## Ngày 4: Tự động hóa Hạ tầng bằng Bash Script (Stored Procedure của OS)

### Bước 1: Khởi tạo File kịch bản (Script)

Trên máy Laptop của chị (hoặc một con VM đóng vai trò là máy điều khiển), mở Terminal và tạo một file mới:

> `nano init_db_node.sh`

*(Lưu ý đuôi `.sh` là quy ước cho file Shell Script, giống `.sql` cho file truy vấn).*

### Bước 2: Viết Code Tự động hóa

Chị copy toàn bộ đoạn mã dưới đây dán vào file `nano` vừa mở. Hãy đọc kỹ các phần comment (bắt đầu bằng dấu `#`) để thấy cách các lệnh `grep`, `awk`, `chmod` được phối hợp thế nào.

```bash
#!/bin/bash
# Dòng trên cùng gọi là 'Shebang', nó báo cho OS biết phải dùng Bash để chạy file này (giống khai báo Engine).

# 1. KHAI BÁO BIẾN (Variables)
SERVER_NAME="db-prod-01"
KEY_PATH="$HOME/.ssh/db_admin_key"

echo "============================================="
echo "🚀 BẮT ĐẦU QUÁ TRÌNH KHỞI TẠO SERVER $SERVER_NAME"
echo "============================================="

# 2. ĐẺ SERVER (Multipass)
echo "[1/4] Đang gọi máy ảo mới..."
multipass launch 24.04 --name $SERVER_NAME --cpus 1 --memory 1G --disk 5G

# 3. LẤY IP TỰ ĐỘNG BẰNG grep VÀ awk (Sức mạnh của Ngày 1)
# multipass info in ra nhiều dòng. Ta dùng grep lọc dòng chữ 'IPv4', sau đó dùng awk lấy cột thứ 2.
echo "[2/4] Đang quét địa chỉ IP..."
SERVER_IP=$(multipass info $SERVER_NAME | grep IPv4 | awk '{print $2}')
echo "✅ IP của Server là: $SERVER_IP"

# 4. TỰ ĐỘNG RÈN KHÓA SSH (Sức mạnh của Ngày 2)
echo "[3/4] Kiểm tra khóa bảo mật SSH..."
if [ ! -f "$KEY_PATH" ]; then
    echo "🔑 Chưa có khóa, đang tiến hành rèn khóa mới..."
    ssh-keygen -t ed25519 -f "$KEY_PATH" -N "" -C "admin@$SERVER_NAME"
else
    echo "🔑 Khóa đã tồn tại, bỏ qua bước rèn khóa."
fi

# 5. ĐẨY KHÓA LÊN SERVER VÀ KHÓA QUYỀN TRUY CẬP (Sức mạnh Ngày 1 + 3)
echo "[4/4] Đang đẩy Public Key lên Server và thiết lập bảo mật (chmod)..."
PUB_KEY=$(cat $KEY_PATH.pub)

# Lệnh multipass exec cho phép đứng từ ngoài bắn thẳng lệnh vào bên trong Server
multipass exec $SERVER_NAME -- bash -c "mkdir -p ~/.ssh && echo '$PUB_KEY' >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"

echo "============================================="
echo "🎉 HOÀN TẤT! HỆ THỐNG ĐÃ SẴN SÀNG."
echo "👉 Để kết nối vào Database Server mà không cần mật khẩu, hãy copy và chạy lệnh sau:"
echo "ssh -i $KEY_PATH ubuntu@$SERVER_IP"
echo "============================================="

```

*Dán xong, nhấn `Ctrl+O` -> `Enter` để lưu, và `Ctrl+X` để thoát.*

### Bước 3: Cấp quyền Thực thi (Execute)

Bây giờ file `init_db_node.sh` chỉ là một file văn bản bình thường. Chị gõ thẳng `./init_db_node.sh` nó sẽ báo lỗi *Permission denied*.

Chị cần cấp quyền `x` (Execute - Quyền chạy) cho nó. Đây chính là bài học Ngày 1:

> `chmod +x init_db_node.sh`

### Bước 4: Chạy Script (Bấm nút Run)

Tận hưởng thành quả tự động hóa. Chị chỉ cần gõ đúng 1 dòng này và đi pha một tách cafe, mọi thứ sẽ tự chạy tuần tự từ trên xuống dưới:

> `./init_db_node.sh`

Khi script chạy xong, nó sẽ in ra màn hình một dòng lệnh `ssh` đã kèm sẵn đường dẫn khóa và IP. Chị chỉ việc copy dòng đó dán vào Terminal là chui thẳng vào Server.

---

### Mở rộng thực tế: Script "Hủy diệt" (Teardown)

Trong dự án thực tế, có code tạo lên thì phải có code đập đi để dọn dẹp môi trường (đặc biệt khi chạy CI/CD pipeline).

Chị tạo thêm một file `destroy_db.sh`:

> `nano destroy_db.sh`

Nội dung cực ngắn:

```bash
#!/bin/bash
SERVER_NAME="db-prod-01"

echo "⚠️ Đang tiêu hủy Server $SERVER_NAME..."
multipass delete $SERVER_NAME
multipass purge
echo "🗑️ Đã dọn dẹp sạch sẽ!"

```

Cấp quyền và chạy:

> `chmod +x destroy_db.sh`
> `./destroy_db.sh`

---

Làm xong bài này, chị đã chính thức hiểu tư duy **Infrastructure as Code (IaC)** ở mức độ nguyên thủy nhất. Khi hệ thống lớn lên, thay vì viết Bash Script dài hàng nghìn dòng rất khó bảo trì, người ta sẽ dùng **Terraform** hoặc **Ansible**.

Nhưng bản chất bên dưới của Terraform và Ansible, cuối cùng cũng chỉ là chạy những lệnh Bash và gọi các API tạo máy chủ y hệt như những gì chị vừa tự tay code ra hôm nay.

Chị chạy thử Script đi xem có lỗi ở dòng nào không!