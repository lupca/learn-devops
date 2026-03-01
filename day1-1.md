Chị đã có kinh nghiệm viết code cứng và hiểu sâu về Database thì việc chuyển sang DevSecOps sẽ nhàn hơn rất nhiều ở khâu tư duy hệ thống.

Thay vì coi Linux là một cái gì đó đen ngòm và xa lạ, bài học này sẽ ánh xạ (map) toàn bộ các lệnh Bash sang các thao tác Database quen thuộc. Mục tiêu của Ngày 1 là tập thói quen **cấm dùng chuột** và làm chủ Terminal giống như cách gõ raw SQL thay vì dùng tool GUI (như DBeaver hay pgAdmin).

Vào việc luôn nhé! Chị mở Terminal lên và gõ theo từng bước dưới đây.

---

## Ngày 1: Sinh tồn trong Bash Terminal - Không chuột, chỉ có lệnh!

Trong thế giới K8s hay Cloud, chị sẽ không có giao diện đồ họa để click đâu. Mọi thứ điều khiển qua một cửa sổ Terminal. Hãy coi hệ thống tệp (File System) của Linux giống như một cụm Database khổng lồ, và các câu lệnh Linux chính là SQL để truy vấn và thao tác.

### 1. Điều hướng và Quản lý "Schema" (ls, cd, mkdir, rm)

Đầu tiên là nhóm lệnh sinh tồn cơ bản nhất để đi lại trong hệ thống. Chị hãy gõ lần lượt các lệnh sau:

* **Kiểm tra vị trí hiện tại:** Gõ `pwd` (Print Working Directory). Trả lời câu hỏi *"Tôi đang ở đâu?"*. Giống như lệnh `SELECT current_database();` trong DB.
* **Tạo thư mục mới:** Gõ `mkdir dev_env` (Make Directory). Tương đương lệnh `CREATE SCHEMA dev_env`.
* **Di chuyển vào thư mục:** Gõ `cd dev_env` (Change Directory). Giống như `USE dev_env;`. Để lùi ra ngoài một cấp, chị gõ `cd ..`
* **Liệt kê dữ liệu:** Gõ `ls -la` (List). Giống như `SHOW TABLES;`. *Mẹo:* Luôn dùng cờ `-la` để xem chi tiết cả file ẩn, dung lượng và quyền hạn thay vì chỉ gõ `ls` trơn.
* **Xóa bỏ (Cực kỳ cẩn thận):** Lùi ra ngoài bằng lệnh `cd ..`, sau đó gõ `rm -rf dev_env`. Lệnh này chính là **DROP** huyền thoại. Nó sẽ xóa sạch sẽ mọi thứ bên trong mà không hỏi một câu nào, tàn bạo y như `DROP DATABASE db_name CASCADE;`. Gõ sai đường dẫn là... bay màu hệ thống.

### 2. Truy vấn dữ liệu văn bản - "SQL" của Terminal (grep, sed, awk)

DevSecOps suốt ngày phải đọc Log. Không ai mở file log 10GB lên bằng Notepad cả. Chị sẽ cần 3 "vũ khí" này để lọc dữ liệu trực tiếp từ Terminal.

**Chuẩn bị môi trường test:** Chị gõ lệnh sau để tạo một file data mẫu:
`echo -e "ID STATUS IP\n1 ERROR 192.168.1.1\n2 OK 10.0.0.1\n3 ERROR 127.0.0.1" > server_log.txt`

**Thực hành truy vấn:**

* **Tìm kiếm với `grep`:** Gõ `grep "ERROR" server_log.txt`.
* *Góc nhìn DB:* Tương đương `SELECT * FROM server_log WHERE line LIKE '%ERROR%';`. Lệnh này rút trích ngay lập tức các dòng chứa từ khóa.


* **Lọc cột với `awk`:** Gõ `awk '{print $1, $3}' server_log.txt`.
* *Góc nhìn DB:* Tương đương `SELECT column1, column3 FROM server_log;`. Cực kỳ mạnh khi file log chia thành các cột (bằng khoảng trắng hoặc dấu phẩy).


* **Tìm và Thay thế với `sed`:** Gõ `sed -i 's/127.0.0.1/0.0.0.0/g' server_log.txt` (Đổi IP localhost thành IP public).
* *Góc nhìn DB:* Tương đương `UPDATE table SET column = REPLACE(column, '127.0.0.1', '0.0.0.0');`. Gõ lại `cat server_log.txt` để xem nó đã được thay đổi chưa.



### 3. Phân quyền - "GRANT/REVOKE" trong Linux (chmod, chown)

Đây là phần cực kỳ quan trọng cho Security. Trong Database, chị cấp quyền cho User/Role được `SELECT`, `INSERT`, hay `UPDATE`. Trong Linux, nó hoạt động tương tự.

Mỗi file trong Linux chia quyền ra làm 3 nhóm đối tượng:

1. **u (User):** Chủ sở hữu file.
2. **g (Group):** Nhóm sở hữu file cùng chung team.
3. **o (Others):** Bất kỳ ai khác trên hệ thống.

Quyền (Permission) có 3 loại cơ bản (được mã hóa bằng số):

* **r (Read) = 4:** Quyền đọc (Giống `GRANT SELECT`).
* **w (Write) = 2:** Quyền ghi/sửa (Giống `GRANT UPDATE, INSERT, DELETE`).
* **x (Execute) = 1:** Quyền chạy file (Dùng cho script hoặc chui vào thư mục).

**Thực hành phân quyền:**

* **Cấp quyền (chmod):** Chị gõ `chmod 755 server_log.txt`. Lệnh này giống `GRANT/REVOKE`. (Giải thích: User có quyền 7 = 4+2+1 tức là đọc+ghi+chạy. Group và Others có quyền 5 = 4+1 tức là đọc+chạy).
* **Đổi chủ (chown):** Lệnh này giống `ALTER TABLE ... OWNER TO ...;`. Ở môi trường thực tế chị sẽ dùng cú pháp dạng `sudo chown root:root server_log.txt` để đổi chủ file sang user root và group root.

---

### 4. Thử thách "Hại não" Tổng hợp

Bây giờ chị hãy tự tay làm bài Lab nhỏ này kết hợp tất cả kiến thức ở trên:

**Bước 1: Tạo dữ liệu giả**
Chạy lệnh này để tạo một file log:

```bash
echo -e "INFO: DB Backup started\nERROR: Password authentication failed for user 'admin'\nINFO: DB Backup finished\nERROR: Disk space full" > db_log.txt

```

**Bước 2: Dùng "SQL" của Linux**
Chị hãy dùng lệnh `grep` để chỉ in ra màn hình những dòng chứa chữ "ERROR". (Yêu cầu tự tìm hiểu: tra Google thêm cờ `-v` của lệnh `grep` để in ra những dòng *KHÔNG* chứa chữ ERROR).

**Bước 3: Tự tước quyền của chính mình**
Gõ lệnh:

```bash
chmod 000 db_log.txt

```

Sau đó thử dùng lệnh `cat db_log.txt` để đọc file. Chị sẽ thấy lỗi kinh điển: **Permission denied**.

**Câu hỏi tư duy để test chị:**

1. Bây giờ file `db_log.txt` đang là `000` (Không ai được đọc, ghi, chạy). Chị dùng lệnh `chmod` nào để cấp lại quyền cho phép chị (Owner) được Đọc và Ghi, nhưng cấm người khác (Group và Others) xem lén file này?
2. Trong hệ thống thực tế, file chứa Mật khẩu kết nối Database (ví dụ `.env`) thì nên để quyền `chmod` là số mấy để an toàn nhất?

---

Phải tự tay gõ lệnh `chmod` rồi bị lỗi `Permission denied` thì mới nhớ lâu được. Chúc chị hoàn thành tốt bài thực hành!