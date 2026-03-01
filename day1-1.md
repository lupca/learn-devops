Chị đã có kinh nghiệm viết code cứng và hiểu sâu về Database thì việc chuyển sang DevSecOps sẽ nhàn hơn rất nhiều ở khâu tư duy hệ thống.

Thay vì coi Linux là một cái gì đó đen ngòm và xa lạ, em sex ánh xạ (map) toàn bộ các lệnh Bash sang các thao tác Database quen thuộc. Mục tiêu của Ngày 1 là tập thói quen **cấm dùng chuột** và làm chủ Terminal giống như cách gõ raw SQL thay vì dùng tool GUI (như DBeaver hay pgAdmin).

Vào việc luôn nhé! Dưới đây là bài học Ngày 1 thiết kế riêng cho chị.

---

## Ngày 1: Sinh tồn trong Bash Terminal - Không chuột, chỉ có lệnh!

Trong thế giới K8s hay Cloud, chị sẽ không có giao diện đồ họa để click đâu. Mọi thứ điều khiển qua một cửa sổ Terminal. Hãy coi hệ thống tệp (File System) của Linux giống như một cụm Database khổng lồ, và các câu lệnh Linux chính là SQL để truy vấn và thao tác.

### 1. Điều hướng và Quản lý "Schema" (ls, cd, mkdir, rm)

Đầu tiên là nhóm lệnh sinh tồn cơ bản nhất để đi lại trong hệ thống.

* `pwd` **(Print Working Directory):** Trả lời câu hỏi *"Tôi đang ở đâu?"*. Giống như lệnh `SELECT current_database();` trong DB.
* `ls` **(List):** Liệt kê các file/thư mục. Giống như `SHOW TABLES;`.
* *Mẹo:* Luôn dùng `ls -la` (xem chi tiết cả file ẩn, dung lượng, quyền hạn).


* `cd` **(Change Directory):** Chuyển thư mục. Giống như `USE database_name;`. `cd ..` là lùi ra ngoài một cấp.
* `mkdir` **(Make Directory):** Tạo thư mục mới. Tương đương `CREATE SCHEMA`.
* `rm` **(Remove):** Xóa file. Đây chính là lệnh **DROP** huyền thoại.
* *Cảnh báo:* Lệnh `rm -rf <thư_mục>` sẽ xóa sạch sẽ mọi thứ bên trong mà không hỏi một câu nào. Nó tàn bạo y như `DROP DATABASE db_name CASCADE;`. Gõ sai đường dẫn là... bay màu hệ thống.



### 2. Truy vấn dữ liệu văn bản - "SQL" của Terminal (grep, sed, awk)

DevSecOps suốt ngày phải đọc Log. Không ai mở file log 10GB lên bằng Notepad cả. Chị sẽ cần 3 "vũ khí" này để lọc dữ liệu trực tiếp từ Terminal.

* `grep` **(Tìm kiếm):** Rút trích các dòng có chứa từ khóa.
* *Góc nhìn DB:* Tương đương với `SELECT * FROM log_file WHERE line LIKE '%ERROR%';`
* *Cách dùng:* `grep "ERROR" /var/log/syslog`


* `awk` **(Xử lý dạng cột):** Cực kỳ mạnh khi file log chia thành các cột (bằng khoảng trắng hoặc dấu phẩy).
* *Góc nhìn DB:* Tương đương với việc chọn cột để xem `SELECT column1, column3 FROM log_file;`
* *Cách dùng:* `awk '{print $1, $3}' file.txt` (In ra cột 1 và cột 3).


* `sed` **(Tìm và Thay thế):**
* *Góc nhìn DB:* Tương đương lệnh `UPDATE table SET column = REPLACE(column, 'old', 'new');`
* *Cách dùng:* `sed -i 's/127.0.0.1/0.0.0.0/g' config.conf` (Đổi IP localhost thành IP public trong file config).



### 3. Phân quyền - "GRANT/REVOKE" trong Linux (chmod, chown)

Đây là phần cực kỳ quan trọng cho Security. Trong Database, chị cấp quyền cho User/Role được `SELECT`, `INSERT`, hay `UPDATE`. Trong Linux, nó hoạt động tương tự.

Mỗi file trong Linux chia quyền ra làm 3 nhóm đối tượng:

1. **u (User):** Chủ sở hữu file.
2. **g (Group):** Nhóm sở hữu file.
3. **o (Others):** Bất kỳ ai khác trên hệ thống.

Quyền (Permission) có 3 loại cơ bản (được mã hóa bằng số):

* **r (Read) = 4:** Quyền đọc (Giống `GRANT SELECT`).
* **w (Write) = 2:** Quyền ghi/sửa (Giống `GRANT UPDATE, INSERT, DELETE`).
* **x (Execute) = 1:** Quyền chạy file (Dùng cho script hoặc chui vào thư mục).

**Các lệnh thực thi:**

* `chown` **(Change Owner):** Đổi chủ sở hữu file. Giống `ALTER TABLE ... OWNER TO ...;`.
* *Cách dùng:* `sudo chown postgres:postgres config.ini` (Đổi chủ file config.ini sang user postgres, group postgres).


* `chmod` **(Change Mode):** Cấp quyền. Giống `GRANT/REVOKE`.
* *Cách dùng:* `chmod 755 script.sh` (User có quyền 7 = 4+2+1 tức là đọc+ghi+chạy. Group và Others có quyền 5 = 4+1 tức là đọc+chạy).



---

### 4. Thử thách "Hại não" cho chị gái

Hãy yêu cầu chị ấy mở Terminal (dùng Multipass hoặc bất kỳ môi trường Linux nào) và làm bài Lab nhỏ này:

**Bước 1: Tạo dữ liệu giả**
Chạy lệnh này để tạo một file log:

```bash
echo -e "INFO: DB Backup started\nERROR: Password authentication failed for user 'admin'\nINFO: DB Backup finished\nERROR: Disk space full" > db_log.txt

```

**Bước 2: Dùng "SQL" của Linux**
Chị hãy dùng lệnh `grep` để chỉ in ra màn hình những dòng chứa chữ "ERROR". (Yêu cầu tìm hiểu thêm cờ `-v` của `grep` để in ra những dòng *KHÔNG* chứa chữ ERROR).

**Bước 3: Tự tước quyền của chính mình**
Gõ lệnh:

```bash
chmod 000 db_log.txt

```

Sau đó thử dùng lệnh `cat db_log.txt` để đọc file. Chị sẽ thấy lỗi kinh điển: **Permission denied**.

**Câu hỏi tư duy để test chị ấy:**

1. Bây giờ file `db_log.txt` đang là `000` (Không ai được đọc, ghi, chạy). Chị dùng lệnh `chmod` nào để cấp lại quyền cho phép chị (Owner) được Đọc và Ghi, nhưng cấm người khác (Group và Others) xem lén file này?
2. Trong hệ thống thực tế, file chứa Mật khẩu kết nối Database (ví dụ `.env`) thì nên để quyền `chmod` là số mấy để an toàn nhất?

---

Phải tự tay gõ lệnh `chmod` rồi bị lỗi `Permission denied` thì mới nhớ lâu được.

Báo kết quả cho em nhé!
