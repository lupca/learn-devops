## Ngày 3.2: Giải phẫu Mạng chuyên sâu - Mô hình 7 tầng (OSI) qua lăng kính Database

Chào chị! Những ngày trước chúng ta mới chỉ lướt qua lớp bề mặt của mạng (IP và Port). Nhưng khi làm DevSecOps, nếu hệ thống sập mà chị chỉ biết ping IP thì sẽ rất bế tắc. Để thực sự bắt đúng bệnh, chị phải hiểu dữ liệu được bọc qua **7 tầng mạng (Mô hình OSI)** như thế nào.

Đừng lo, nó không phải lý thuyết suông. Hãy nhìn nó dưới góc độ của một người làm Database: Khi một con App gửi lệnh `SELECT * FROM users` xuống DB, câu lệnh đó phải đi qua 7 bước đóng gói trước khi chui vào đường dây mạng.

### 1. Bóc tách 7 Tầng Mạng (Từ đỉnh xuống đáy)

> **📊 Sơ đồ hành trình câu SQL đi qua 7 tầng mạng:**

```mermaid
graph TB
    subgraph journey["🚀 Hành trình của câu: SELECT * FROM users"]
        direction TB
        APP["<b>Tầng 7 — Application</b><br/>🐘 Câu SQL gốc: SELECT * FROM users<br/>Giao thức: PostgreSQL Protocol"]
        PRES["<b>Tầng 6 — Presentation</b><br/>🔐 Mã hóa SSL/TLS + Encode UTF-8<br/>Câu SQL giờ thành chuỗi mã hóa"]
        SESS["<b>Tầng 5 — Session</b><br/>🔗 Mở Connection #42 trong Pool<br/>Duy trì phiên kết nối App ↔ DB"]
        TRANS["<b>Tầng 4 — Transport</b><br/>📦 Cắt thành TCP Segments<br/>Gắn Port nguồn :54321 → đích :5432"]
        NET["<b>Tầng 3 — Network</b><br/>🗺️ Gắn IP nguồn 10.0.0.5 → đích 10.0.0.10<br/>Router tìm đường đi"]
        DATA["<b>Tầng 2 — Data Link</b><br/>🏷️ Gắn MAC Address<br/>Switch phân phối trong mạng LAN"]
        PHY["<b>Tầng 1 — Physical</b><br/>⚡ Tín hiệu điện / ánh sáng<br/>Chạy trên cáp quang / WiFi"]
    end

    APP -->|"đóng gói ↓"| PRES
    PRES -->|"đóng gói ↓"| SESS
    SESS -->|"đóng gói ↓"| TRANS
    TRANS -->|"đóng gói ↓"| NET
    NET -->|"đóng gói ↓"| DATA
    DATA -->|"đóng gói ↓"| PHY

    PHY -.->|"🔌 Qua dây mạng đến DB Server"| PHY2["⚡ DB Server nhận tín hiệu"]
    PHY2 -.->|"mở gói ↑ ngược lại 7 tầng"| APP2["🐘 PostgreSQL nhận được:<br/>SELECT * FROM users"]

    style APP fill:#E3F2FD,stroke:#1565C0,stroke-width:2px
    style PRES fill:#E8EAF6,stroke:#283593,stroke-width:2px
    style SESS fill:#F3E5F5,stroke:#6A1B9A,stroke-width:2px
    style TRANS fill:#FFF3E0,stroke:#E65100,stroke-width:2px
    style NET fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
    style DATA fill:#FFF9C4,stroke:#F9A825,stroke-width:2px
    style PHY fill:#FFEBEE,stroke:#C62828,stroke-width:2px
    style APP2 fill:#C8E6C9,stroke:#1B5E20,stroke-width:2px
    style PHY2 fill:#FFCDD2,stroke:#B71C1C
```

> 💡 **Đọc sơ đồ:** App gửi câu SQL → bọc 7 lớp vỏ → chạy qua dây mạng → DB Server bóc 7 lớp vỏ ngược lại → nhận được câu SQL gốc!

| Tầng (Layer) | Tên gọi | Chức năng (Góc nhìn Database) | Lỗi thường gặp & Cách check |
| --- | --- | --- | --- |
| **7** | **Application (Ứng dụng)** | Dữ liệu thực tế. Chứa chính xác câu SQL của chị, sử dụng giao thức PostgreSQL/MySQL. | Sai cú pháp SQL, sai DB name. Check log của Database. |
| **6** | **Presentation (Trình diễn)** | Định dạng và mã hóa dữ liệu. Ép kiểu chuỗi (UTF-8) hoặc mã hóa kết nối bằng chứng chỉ SSL/TLS. | Lỗi "SSL connection has been closed". Check cấu hình chứng chỉ mạng. |
| **5** | **Session (Phiên)** | Duy trì kết nối. Quản lý việc App mở bao nhiêu connection xuống DB. Giống như Connection Pool (PgBouncer). | Lỗi "Too many connections" hoặc "Connection timeout". |
| **4** | **Transport (Giao vận)** | Quản lý truyền tải bằng cổng (Port 5432, 3306). Cắt câu SQL dài thành nhiều mảnh nhỏ và đánh số thứ tự (TCP) để không bị mất chữ. | Cổng đóng, chặn Firewall. Check bằng `telnet <IP> <Port>`. |
| **3** | **Network (Mạng)** | Gắn địa chỉ IP nguồn và đích. Tìm đường đi ngắn nhất qua các Router để App ở mạng này tìm được DB ở mạng kia. | Sai IP, không định tuyến được. Check bằng `ping` hoặc `ip route`. |
| **2** | **Data Link (Liên kết)** | Phân phối trong cùng một mạng LAN nội bộ. Gắn địa chỉ phần cứng MAC. | Lỗi do Switch hoặc trùng địa chỉ MAC (hiếm gặp trên Cloud). |
| **1** | **Physical (Vật lý)** | Dây cáp quang, tín hiệu điện, card mạng vật lý. | Đứt cáp quang biển, lỏng dây mạng, server mất điện. |

**Tư duy Debug hệ thống:**
Khi con App kêu gào *"Tao không gọi được Database"*, chị tuyệt đối không mò mẫm lung tung. Hãy test từ dưới lên trên (Bottom-Up):

> **📊 Sơ đồ quy trình debug mạng — Từ dưới lên trên:**

```mermaid
flowchart TB
    START["🚨 App báo:<br/><i>'Không kết nối được Database!'</i>"]

    subgraph step1["🔍 BƯỚC 1 — Kiểm tra Lớp 3 (Network)"]
        CMD1["💻 Gõ lệnh:<br/><code>ping 10.0.0.10</code>"]
        Q1{"Ping có<br/>thông không?"}
        ERR1["❌ Lỗi Lớp 3<br/>🔧 Sai IP / Sai Subnet<br/>Sai Route / Mất mạng"]
    end

    subgraph step2["🔍 BƯỚC 2 — Kiểm tra Lớp 4 (Transport)"]
        CMD2["💻 Gõ lệnh:<br/><code>telnet 10.0.0.10 5432</code><br/>hoặc <code>nc -zv 10.0.0.10 5432</code>"]
        Q2{"Port có<br/>mở không?"}
        ERR2["❌ Lỗi Lớp 4<br/>🔧 Firewall chặn port<br/>DB chưa start / Sai port"]
    end

    subgraph step3["🔍 BƯỚC 3 — Kiểm tra Lớp 7 (Application)"]
        CMD3["💻 Dùng client:<br/><code>psql -h 10.0.0.10 -U admin -d mydb</code>"]
        Q3{"Đăng nhập<br/>được không?"}
        ERR3["❌ Lỗi Lớp 7<br/>🔧 Sai user/pass / Hết pool<br/>pg_hba.conf chặn / Sai DB name"]
    end

    OK["✅ Kết nối OK!<br/>Lỗi nằm ở code App"]

    START --> CMD1 --> Q1
    Q1 -->|"❌ Không"| ERR1
    Q1 -->|"✅ Có"| CMD2 --> Q2
    Q2 -->|"❌ Không"| ERR2
    Q2 -->|"✅ Có"| CMD3 --> Q3
    Q3 -->|"❌ Không"| ERR3
    Q3 -->|"✅ Có"| OK

    style START fill:#FFCDD2,stroke:#C62828,stroke-width:2px
    style step1 fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
    style step2 fill:#FFF3E0,stroke:#E65100,stroke-width:2px
    style step3 fill:#E3F2FD,stroke:#1565C0,stroke-width:2px
    style ERR1 fill:#EF5350,stroke:#B71C1C,color:#fff
    style ERR2 fill:#EF5350,stroke:#B71C1C,color:#fff
    style ERR3 fill:#EF5350,stroke:#B71C1C,color:#fff
    style OK fill:#66BB6A,stroke:#1B5E20,color:#fff
```

1. **Lớp 3:** Ping có thông IP không? (Nếu ping xịt -> Lỗi định tuyến/Subnet).
2. **Lớp 4:** Telnet/nc vào cái Port của DB có mở không? (Nếu port đóng -> Lỗi Firewall hoặc DB chưa chạy).
3. **Lớp 7:** Dùng app client (như DBeaver/psql) test kết nối bằng user/pass xem có vào được không? (Nếu báo sai mật khẩu/hết pool -> Lỗi cấu hình App/DB).

---

### 2. Thực hành: Thao túng Lớp 3 (Network) với DNS

Ở lớp 3, các máy móc gọi nhau bằng IP. Nhưng ứng dụng thì cấu hình bằng tên miền (ví dụ: `db.internal.local`). Hệ điều hành dùng một file cực kỳ quyền lực để ép tên miền thành IP, đó là file `/etc/hosts`.

> **📊 Sơ đồ: Trước và sau khi sửa /etc/hosts:**

```mermaid
flowchart LR
    subgraph before["🌐 TRƯỚC KHI SỬA — Bình thường"]
        direction TB
        APP1["💻 Máy chị gõ:<br/><code>ping google.com</code>"]
        DNS1["🗂️ /etc/hosts<br/><i>Không có dòng nào về google</i>"]
        REAL_DNS["☁️ DNS Server thật<br/>tra cứu google.com"]
        REAL_IP["📍 Kết quả:<br/><b>142.250.72.14</b><br/>(IP thật của Google)"]
        APP1 --> DNS1
        DNS1 -->|"không thấy → hỏi DNS"| REAL_DNS --> REAL_IP
    end

    subgraph after["🔧 SAU KHI SỬA — Thao túng DNS"]
        direction TB
        APP2["💻 Máy chị gõ:<br/><code>ping google.com</code>"]
        DNS2["🗂️ /etc/hosts<br/><b>127.0.0.1 google.com</b><br/>⚡ Ép cứng!"]
        FAKE_IP["📍 Kết quả:<br/><b>127.0.0.1</b><br/>(Trỏ về chính máy mình!)"]
        APP2 --> DNS2
        DNS2 -->|"thấy rồi → dùng luôn!"| FAKE_IP
    end

    style before fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
    style after fill:#FFF3E0,stroke:#E65100,stroke-width:2px
    style REAL_IP fill:#C8E6C9,stroke:#1B5E20
    style FAKE_IP fill:#FFCC80,stroke:#E65100
    style DNS2 fill:#FFE0B2,stroke:#EF6C00,stroke-width:2px
```

> 💡 **Ứng dụng thực tế:** Trong K8s, nếu CoreDNS chết, DevSecOps có thể ép file `/etc/hosts` trong Pod trỏ thẳng IP Database để cứu hệ thống tạm thời!

Chị hãy mở Terminal chui vào con VM đang có, và làm thao tác thao túng DNS này:

1. Gõ `ping google.com` (Nó sẽ ra IP thật của Google). Ấn Ctrl+C dừng lại.
2. Dùng quyền root mở file cấu hình gốc:
> `sudo nano /etc/hosts`


3. Thêm dòng này vào cuối cùng (Ép Google trỏ về máy ảo nội bộ):
> `127.0.0.1 google.com`


4. Lưu lại (Ctrl+O -> Enter -> Ctrl+X).
5. Gõ lại `ping google.com`. Chị sẽ thấy nó ping thẳng vào `127.0.0.1`.

**Thực tế dự án:** Trong K8s, nếu hệ thống phân giải tên (CoreDNS) bị chết, các Pod không tìm thấy DB. DevSecOps có thể dùng trò này để ép cứng file `/etc/hosts` bên trong Pod trỏ thẳng về IP của Database để cứu hệ thống tạm thời! *(Nhớ vào xóa dòng vừa thêm kẻo máy mất mạng nhé).*

---

### 3. Thực hành: Soi rọi Lớp 4 và Lớp 7 bằng `tcpdump`

Khi Dev khăng khăng: *"Code em gửi đúng câu INSERT rồi mà DB chị không nhận!"*, chị không cần cãi nhau mồm. Chị lôi máy quét mã vạch của Linux ra: `tcpdump`. Nó bắt tận tay mọi gói tin ở Lớp 4 (Port) và hiển thị nội dung bên trong Lớp 7 (Application).

> **📊 Sơ đồ thí nghiệm tcpdump — 3 Terminal cùng lúc:**

```mermaid
flowchart TB
    subgraph setup["🧪 THÍ NGHIỆM BẮT GÓI TIN"]
        direction TB
        
        subgraph t1["🖥️ Terminal 1 — Giả làm DB Server"]
            NC["<code>nc -l 8888</code><br/>📡 Mở cổng 8888 chờ nhận data<br/><i>(Đóng vai Database)</i>"]
        end

        subgraph t2["🖥️ Terminal 2 — Máy quay lén"]
            TCP["<code>sudo tcpdump -i any port 8888 -n -A</code><br/>🔍 Soi mọi gói tin qua cổng 8888<br/><i>(Camera an ninh)</i>"]
        end

        subgraph t3["🖥️ Terminal 3 — App gửi SQL"]
            CLIENT["<code>echo 'SELECT * FROM users<br/>WHERE id = 1;' | nc IP 8888</code><br/>📤 Bắn câu SQL từ laptop"]
        end

        subgraph result["📋 KẾT QUẢ TRÊN TERMINAL 2"]
            L4["<b>Lớp 4 (Transport):</b><br/>📦 IP nguồn: 192.168.1.5:54321<br/>📦 IP đích: 10.0.0.10:8888<br/>🏁 Cờ TCP: [S], [.], [P.]"]
            L7["<b>Lớp 7 (Application):</b><br/>📝 <code>SELECT * FROM users WHERE id = 1;</code><br/>👀 Nguyên văn câu SQL!"]
        end
    end

    t3 -->|"📨 Gửi gói tin"| t1
    t2 -.->|"🔍 Bắt được!"| result
    L4 --> L7

    style t1 fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
    style t2 fill:#FFF3E0,stroke:#E65100,stroke-width:2px
    style t3 fill:#E3F2FD,stroke:#1565C0,stroke-width:2px
    style result fill:#F3E5F5,stroke:#6A1B9A,stroke-width:2px
    style L4 fill:#FFE0B2,stroke:#E65100
    style L7 fill:#C8E6C9,stroke:#1B5E20,stroke-width:2px
```

> 💡 **Kết luận:** Thấy gói tin trên tcpdump → mạng OK, lỗi do DB. Không thấy gì → Firewall chặn, gói tin chưa đến được Server!

**Bước 1: Cài đặt công cụ** (Trên con VM)

> `sudo apt update && sudo apt install -y tcpdump`

**Bước 2: Giả lập một Database Server đang mở cổng**
Mở Tab Terminal số 1 (chui vào VM), dùng lệnh netcat mở cổng 8888:

> `nc -l 8888`
> *(Để im đó, nó đang đóng vai Database chờ request).*

**Bước 3: Đặt máy quay lén ở Card mạng**
Mở Tab Terminal số 2 (cũng chui vào VM), chạy tcpdump bằng quyền root:

> `sudo tcpdump -i any port 8888 -n -A`
> *(Lệnh này soi mọi thứ qua cổng 8888, in ra dưới dạng chữ đọc được `-A`).*

**Bước 4: Bắn truy vấn từ xa**
Mở Tab Terminal số 3 (Trên máy tính Laptop của chị, ở ngoài VM). Bắn một câu lệnh vào cái cổng 8888 đó:

> `echo "SELECT * FROM users WHERE id = 1;" | nc <IP_CUA_VM> 8888`

**Nghiệm thu bắt quả tang:**
Chị quay lại cái Tab số 2 đang chạy `tcpdump`. Màn hình sẽ nhảy một loạt thông tin Lớp 4 (Địa chỉ IP nguồn, IP đích, cờ TCP). Nếu kéo lên và nhìn kỹ, chị sẽ thấy nguyên văn câu `SELECT * FROM users WHERE id = 1;` chình ình ở đó (Dữ liệu Lớp 7).

Nếu chị thấy gói tin tới -> Mạng bình thường, lỗi do DB. Nếu chị không thấy bảng tcpdump nhảy số -> Lớp 3 hoặc Lớp 4 bị chặn (Firewall), gói tin chưa từng đến được Server.

*(Ấn Ctrl+C ở các tab để dọn dẹp).*

---

Làm chủ được mô hình 7 tầng này, chị sẽ có tư duy phân lập lỗi cực kỳ sắc bén. Gặp bug mạng nào cũng chia để trị, khoanh vùng chính xác lớp đang hỏng.

Chị chạy test thử cái `tcpdump` đi. Nếu ổn rồi, chúng ta sẽ kết thúc chuỗi kiến thức máy chủ trần trụi (Bare-metal) ở đây.