## Ngày 2.1: Thuật "Phân thân" Server với Multipass

Chào chị. Hôm qua chị đã biết cách tự tay khóa trái cửa con Server bằng SSH Key rồi. Nhưng làm DevSecOps hay Cloud, không ai đi cài OS bằng tay hay dùng mấy phần mềm nặng nề như VMware/VirtualBox cả. Nó quá chậm.

Hôm nay, chúng ta học cách đẻ ra một con Server mới tinh trong vòng chưa tới 1 phút, và xóa sổ nó cũng nhanh y như cách chị gõ `DROP DATABASE db_name;`. Công cụ chúng ta dùng là **Multipass** (của Canonical - cha đẻ Ubuntu). Hãy coi nó như một cỗ máy đẻ Server siêu tốc dùng dòng lệnh.

### 1. Ánh xạ khái niệm

| Khái niệm Multipass/Cloud | Góc nhìn Database | Giải thích |
| --- | --- | --- |
| **Virtual Machine (VM)** | **Database Instance** | Một hệ điều hành độc lập chạy trên máy thật, có CPU, RAM, Ổ cứng riêng. |
| **Image (Ubuntu 22.04, 24.04)** | **DB Engine Version** | Phiên bản gốc. Chị muốn đẻ ra bản PostgreSQL 14 hay 16? |
| **multipass launch** | **CREATE DATABASE** | Khởi tạo một con Server mới tinh từ Image. |
| **multipass delete & purge** | **DROP DATABASE ... CASCADE** | Xóa sổ hoàn toàn con Server không để lại dấu vết. |

---

### 2. Thực hành: Trở thành "Kẻ kiến tạo"

**Bước 1: Cài đặt Multipass**
Chị tự Google cách tải Multipass cho hệ điều hành đang dùng (Windows/Mac/Linux) nhé. Cài xong, mở Terminal lên và chiến.

**Bước 2: Xem danh mục "Hàng hóa"**
Giống như xem có những phiên bản DB nào hỗ trợ, gõ:

```bash
multipass find

```

Chị sẽ thấy một danh sách các bản Ubuntu (20.04, 22.04, 24.04).

**Bước 3: Khai sinh Server đầu lòng**
Gõ lệnh sau để tạo một con VM có tên là `db-node-01`, cấp cho nó 2 CPU, 2GB RAM và 10GB Ổ cứng:

```bash
multipass launch 24.04 --name db-node-01 --cpus 2 --memory 2G --disk 10G

```

Chờ khoảng 30s - 1 phút. Bùm! Chị đã có một con Server Linux hoàn chỉnh.

**Bước 4: Kiểm kê tài sản**
Để xem tất cả Server đang chạy (giống lệnh `\l` trong psql hoặc `SHOW DATABASES`), chị gõ:

```bash
multipass list

```

Ghi nhớ lại cái **Địa chỉ IP (IPv4)** của con `db-node-01` nhé. Nó cực kỳ quan trọng.

**Bước 5: Thâm nhập Server**
Cách nhanh nhất của Multipass để chui thẳng vào quyền root của con VM vừa tạo:

```bash
multipass shell db-node-01

```

Bây giờ dấu nhắc lệnh của chị đã đổi thành `ubuntu@db-node-01`. Chị đang đứng bên trong con Server đó. Gõ thử `ls -la` hoặc `ip addr` (bài Ngày 1) để kiểm tra. Xong xuôi thì gõ `exit` để thoát ra máy thật.

---

### 3. Ghép nối kiến thức: Bơm SSH Key của Ngày 2 vào con VM mới

Lệnh `multipass shell` ở trên là dùng "cửa sau" của Multipass. Trong thực tế (AWS, Google Cloud), chị phải dùng SSH chuẩn. Bây giờ chúng ta sẽ nhét cái "Ổ khóa" (Public Key) hôm qua chị tạo vào con `db-node-01` này.

**Cách làm:**

1. Trên máy thật, in cái ổ khóa ra màn hình và copy nó:
```bash
cat ~/.ssh/id_ed25519.pub

```


2. Chui vào VM bằng lệnh của Multipass:
```bash
multipass shell db-node-01

```


3. Mở file chìa khóa của VM lên (user mặc định của Multipass luôn là `ubuntu`):
```bash
nano ~/.ssh/authorized_keys

```


4. Paste cái Public Key của chị xuống **dòng cuối cùng** của file này. Lưu lại (Ctrl+O -> Enter -> Ctrl+X).
5. Gõ `exit` để thoát ra máy thật.

**Nghiệm thu:**
Bây giờ từ máy thật, chị hãy dùng chuẩn giao thức SSH để kết nối vào IP của con VM (lấy IP từ lệnh `multipass list`):

```bash
ssh ubuntu@<IP_cua_db-node-01>

```

Nếu nó cho chị vào thẳng mà không đòi mật khẩu, xin chúc mừng, chị đã hoàn thành kỹ năng cơ bản nhất của một kỹ sư Cloud: **Provisioning & Access Management**.

---

### 4. Thuật Hủy diệt (Dọn dẹp chiến trường)

Không dùng nữa thì phải xóa đi cho nhẹ máy (hoặc đỡ tốn tiền Cloud).
Để xóa con VM:

```bash
multipass delete db-node-01

```

Lúc này nó mới nằm trong "Thùng rác" (Trạng thái Deleted). Để dọn dẹp triệt để giải phóng ổ cứng (giống lệnh `VACUUM` trong Postgres), gõ:

```bash
multipass purge

```

Gõ `multipass list` lại, chị sẽ thấy sạch bóng quân thù.

---

**Thử thách cuối ngày:**
Chị hãy dùng lệnh `launch` để tạo cùng lúc 2 con VM tên là `db-master` và `db-slave`.
Chui vào con `db-master`, thử gõ lệnh `ping <IP_cua_con_db-slave>` xem hai con Server này có nhìn thấy nhau trong hệ thống mạng không?

Làm xong bài này, báo lại kết quả.