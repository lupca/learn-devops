Chào chị. Hôm trước chúng ta đã thử kéo cáp mạng để một con App giả lập gọi được Database. Nhưng đó mới chỉ là bề nổi của tảng băng chìm.

Trong DevSecOps và thiết kế kiến trúc hệ thống, tùy vào yêu cầu về **Bảo mật (Security)** hoặc **Hiệu năng (Performance)**, chúng ta không chỉ dùng một loại mạng. Docker cung cấp nhiều loại "Card mạng" (Network Drivers) khác nhau để chị thiết kế các mô hình vùng kín (Air-gapped) hoặc tối ưu hóa tốc độ truy vấn Database.

Bài hôm nay sẽ lật mở toàn bộ các mô hình mạng của Docker.

---

## Ngày 5 - Buổi 2: Giải phẫu các kiến trúc mạng Docker

Hãy coi máy chủ Linux của chị như một tòa nhà văn phòng. Docker cho phép chị đi dây mạng cho các Container theo 4 mô hình chính sau:

> **📊 Sơ đồ tổng quan 4 mô hình mạng Docker:**

```mermaid
graph TB
    subgraph overview["🏢 MÁY CHỦ LINUX (Tòa nhà văn phòng)"]
        direction TB

        subgraph bridge_box["🌉 BRIDGE — Mạng LAN riêng (Mặc định)"]
            BR_SW["🔌 Switch ảo docker0<br/>Subnet: 172.17.0.0/16"]
            BR_C1["📦 Web App<br/>172.17.0.2"]
            BR_C2["📦 PostgreSQL<br/>172.17.0.3"]
            BR_SW --- BR_C1
            BR_SW --- BR_C2
            BR_C1 <-->|"gọi bằng TÊN"| BR_C2
            BR_NAT["🚪 NAT -p 8080:80<br/>Cổng bảo vệ ra ngoài"]
        end

        subgraph host_box["🏠 HOST — Chung mạng máy thật"]
            HOST_NIC["🖥️ Card mạng máy thật<br/>IP: 192.168.1.100"]
            HOST_C["📦 PostgreSQL<br/>Dùng trực tiếp IP máy thật<br/>⚡ Không NAT = Nhanh nhất"]
            HOST_NIC --- HOST_C
        end

        subgraph none_box["🔒 NONE — Cách ly hoàn toàn"]
            NONE_C["📦 Tool mã hóa<br/>🚫 Không có card mạng<br/>🚫 Không IP, không Internet<br/>Chỉ có localhost"]
            NONE_V["📁 Volume<br/>Xuất file ra đây"]
            NONE_C -.-> NONE_V
        end

        subgraph macvlan_box["🏷️ MACVLAN — MAC thật trên LAN"]
            MAC_C["📦 Container<br/>MAC: aa:bb:cc:dd:ee:ff<br/>IP: 192.168.1.201<br/>Ngang hàng với máy thật"]
        end
    end

    INTERNET["🌐 Internet / Mạng công ty"]
    INTERNET <-->|"qua NAT"| BR_NAT
    INTERNET <-->|"trực tiếp"| HOST_NIC
    INTERNET x--x|"❌ bị chặn"| NONE_C
    INTERNET <-->|"như máy vật lý"| MAC_C

    style bridge_box fill:#E3F2FD,stroke:#1565C0,stroke-width:2px
    style host_box fill:#FFF3E0,stroke:#E65100,stroke-width:2px
    style none_box fill:#FFEBEE,stroke:#C62828,stroke-width:2px
    style macvlan_box fill:#F3E5F5,stroke:#6A1B9A,stroke-width:2px
    style INTERNET fill:#E0E0E0,stroke:#424242,stroke-width:2px
```

> 💡 **Nhìn 1 phát là hiểu:** Bridge = mạng LAN riêng có cổng bảo vệ | Host = bán vỉa hè, không rào chắn | None = két sắt bị rút dây mạng | Macvlan = giả làm máy thật

### 1. Bridge (Mạng Cầu Nối - VLAN ảo)

* **Bản chất:** Đây là loại mạng mặc định. Docker tạo ra một cái Switch ảo (docker0). Các Container cắm chung vào cái Switch này sẽ được cấp IP nội bộ (ví dụ `172.17.x.x`).
* **Góc nhìn thực tế:** Giống như lập một mạng LAN riêng cho phòng Kế toán. Các máy trong phòng tự gọi nhau bằng Tên (Hostname) thay vì IP. Người ngoài muốn vào phải xin phép qua cổng bảo vệ (NAT Port-mapping bằng cờ `-p`).
* **Sử dụng:** 90% ứng dụng thông thường (Web App gọi xuống Database).

> **📊 Sơ đồ chi tiết Bridge Network — Phòng Kế toán có cổng bảo vệ:**

```mermaid
graph TB
    subgraph host_machine["🖥️ MÁY CHỦ THẬT (Host)"]
        subgraph bridge_net["🌉 Bridge Network 'my_vpc' — Subnet 172.18.0.0/16"]
            DNS_INT["🗂️ DNS nội bộ Docker<br/><i>Tự động phân giải tên ↔ IP</i>"]
            
            subgraph app_c["📦 Container: web-app"]
                APP["🌐 Node.js App<br/>IP: 172.18.0.2<br/>Port nội bộ: 3000"]
                APP_CODE["Code kết nối DB:<br/><code>host: 'db-core'</code><br/><code>port: 5432</code><br/>👆 Gọi bằng TÊN!"]
            end
            
            subgraph db_c["📦 Container: db-core"]
                DB["🐘 PostgreSQL<br/>IP: 172.18.0.3<br/>Port nội bộ: 5432"]
            end

            DNS_INT -.->|"db-core → 172.18.0.3"| APP
            APP <-->|"🔗 Kết nối nội bộ<br/>Gọi bằng tên 'db-core'"| DB
        end
        
        NAT["🚪 NAT Gateway<br/><code>-p 8080:3000</code><br/>Người ngoài vào port 8080<br/>→ chuyển vào Container port 3000"]
    end

    USER["👤 Người dùng truy cập<br/>http://192.168.1.100:<b>8080</b>"]
    USER -->|"Request đi vào"| NAT
    NAT -->|"Chuyển tiếp"| APP

    style bridge_net fill:#E3F2FD,stroke:#1565C0,stroke-width:2px
    style app_c fill:#BBDEFB,stroke:#0D47A1
    style db_c fill:#BBDEFB,stroke:#0D47A1
    style NAT fill:#FFE0B2,stroke:#E65100,stroke-width:2px
    style USER fill:#E0E0E0,stroke:#424242
    style DNS_INT fill:#FFF9C4,stroke:#F9A825
```

> 💡 **Điểm quan trọng:** Trong Bridge, App gọi DB bằng **tên Container** (không cần nhớ IP). Người ngoài chỉ vào được qua cổng NAT `-p`.

### 2. Host (Mạng Chung Chạ - Tối đa Hiệu năng)

* **Bản chất:** Container đập bỏ hoàn toàn vách ngăn mạng ảo. Nó sử dụng trực tiếp Card mạng và dải IP của chính máy chủ thật (Host).
* **Góc nhìn thực tế:** Thay vì thuê ki-ốt trong trung tâm thương mại, chị mang bàn ra vỉa hè bày bán luôn. Khách (Request) đi thẳng vào không qua cửa từ hay thang máy nào cả. Không có độ trễ do NAT.
* **Sử dụng:** Rất hay dùng cho Database chịu tải cực cao. Chị không muốn độ trễ mạng ảo làm chậm đi vài mili-giây của các câu lệnh Query phức tạp.

> **📊 Sơ đồ chi tiết Host Network — Bán hàng vỉa hè, không qua trung gian:**

```mermaid
graph TB
    subgraph host_machine["🖥️ MÁY CHỦ THẬT — IP: 192.168.1.100"]
        NIC["🔌 Card mạng thật eth0<br/>IP: 192.168.1.100"]
        
        subgraph container["📦 Container: db-fast (--network host)"]
            PG["🐘 PostgreSQL<br/>Mở port 5432<br/>⚡ Dùng TRỰC TIẾP card mạng thật<br/>❌ Không có IP ảo riêng<br/>❌ Không cần cờ -p"]
        end
        
        NIC ---|"dùng chung 100%"| PG
    end

    subgraph compare["⚖️ SO SÁNH TỐC ĐỘ"]
        BRIDGE_SPEED["🌉 Bridge: Request → NAT → Switch ảo → Container<br/>⏱️ Thêm ~0.1-0.5ms mỗi query"]
        HOST_SPEED["🏠 Host: Request → Container<br/>⚡ 0ms overhead — Nhanh nhất!"]
    end

    CLIENT["👤 Client kết nối<br/>psql -h 192.168.1.100 -p 5432<br/>→ Đi thẳng vào DB!"]
    CLIENT -->|"Không qua NAT"| NIC

    style container fill:#FFF3E0,stroke:#E65100,stroke-width:2px
    style host_machine fill:#FFF9C4,stroke:#F9A825,stroke-width:2px
    style CLIENT fill:#E0E0E0,stroke:#424242
    style BRIDGE_SPEED fill:#FFCDD2,stroke:#C62828
    style HOST_SPEED fill:#C8E6C9,stroke:#1B5E20
    style compare fill:#F5F5F5,stroke:#9E9E9E,stroke-width:2px
```

> 💡 **Khi nào dùng Host?** Database chịu tải cao, cần mỗi mili-giây. Nhưng đánh đổi: mất cách ly mạng, 2 Container không thể cùng dùng 1 port.

### 3. None (Mạng Cách Ly - Két sắt tuyệt mật)

* **Bản chất:** Container sinh ra không có card mạng (ngoài cái `localhost` của chính nó). Hoàn toàn mù tịt với Internet và các Container khác.
* **Góc nhìn thực tế:** Giống như một cái máy tính bị rút hẳn dây mạng, dùng để xử lý dữ liệu tuyệt mật. Hacker dù có khai thác được lỗ hổng của ứng dụng chui vào trong, cũng không thể truyền dữ liệu (Data Exfiltration) ra ngoài.
* **Sử dụng:** Các Job xử lý dữ liệu nhạy cảm (ví dụ: Tool mã hóa mật khẩu, đọc file sao kê ngân hàng nội bộ). Xử lý xong xuất ra file Volume rồi tự hủy.

> **📊 Sơ đồ chi tiết None Network — Két sắt bị rút dây mạng:**

```mermaid
graph TB
    subgraph host_machine["🖥️ MÁY CHỦ THẬT"]
        subgraph container["📦 Container (--network none)"]
            TOOL["🔐 Tool mã hóa mật khẩu"]
            LO["🔄 Chỉ có card lo<br/>127.0.0.1 (localhost)"]
            NO_ETH["🚫 Không có eth0<br/>🚫 Không có IP ngoài<br/>🚫 Không DNS"]
            TOOL --- LO
            TOOL --- NO_ETH
        end
        
        VOL_OUT["📁 Volume<br/>Đầu ra duy nhất:<br/>Xuất file đã mã hóa"]
        container -.->|"📄 Ghi file ra Volume"| VOL_OUT
    end

    INTERNET["🌐 Internet"]
    HACKER["🏴‍☠️ Hacker"]
    OTHER_C["📦 Container khác"]
    
    INTERNET x--x|"❌ Không thể vào"| container
    HACKER x--x|"❌ Không truyền<br/>data ra được"| container
    OTHER_C x--x|"❌ Không thấy nhau"| container

    style container fill:#FFEBEE,stroke:#C62828,stroke-width:2px
    style host_machine fill:#FFF9C4,stroke:#F9A825,stroke-width:2px
    style INTERNET fill:#E0E0E0,stroke:#424242
    style HACKER fill:#424242,stroke:#000,color:#fff
    style OTHER_C fill:#BBDEFB,stroke:#0D47A1
    style VOL_OUT fill:#C8E6C9,stroke:#1B5E20
    style NO_ETH fill:#EF5350,stroke:#B71C1C,color:#fff
```

> 💡 **Ứng dụng DevSecOps:** Xử lý sao kê ngân hàng, mã hóa password, sinh chứng chỉ SSL → nhét vào Container `none`, xuất file qua Volume. Hacker chui vào cũng không gửi data ra ngoài được!

### 4. Macvlan (Mạng Vật Lý ảo - Cao cấp)

* **Bản chất:** Cấp cho Container một địa chỉ MAC vật lý. Container xuất hiện trên mạng cty (mạng cục bộ của router thật) như một cái máy tính vật lý bình thường, ngang hàng với chính máy chủ Host.
* **Sử dụng:** Dành cho các hệ thống Legacy (đồ cổ) yêu cầu thiết bị phải có địa chỉ MAC thật. Ít dùng trong DevSecOps hiện đại.

---

### 2. Thực hành: Trải nghiệm 3 trạng thái Mạng

Chị hãy mở Terminal lên. Chúng ta sẽ làm bài Lab so sánh để thấy sự khác biệt về mặt cấu trúc lệnh.

**Test 1: Mạng Không Khí (Air-gapped) với `none**`
Chị đẻ một môi trường Linux siêu nhỏ gọn (alpine) để test, ép nó vào mạng `none` và chui thẳng vào trong:

> `docker run -it --rm --network none alpine sh`

Bên trong Container, chị kiểm tra các card mạng hiện có:

> `ip addr`
> *(Chị sẽ chỉ thấy card `lo` - 127.0.0.1. Không có IP nào khác).*

Thử gõ lệnh gọi ra Internet:

> `ping google.com`
> *(Kết quả: `ping: bad address`. Hệ thống hoàn toàn cách ly). Gõ `exit` để thoát và tự hủy Container.*

**Test 2: Mạng Hiệu năng cao với `host**`
Bây giờ, chị đẻ ra một con PostgreSQL, nhưng yêu cầu nó hòa mạng chung với máy chủ thật:

> `docker run --name db-fast --network host -e POSTGRES_PASSWORD=sieumat -d postgres:15`

*Lưu ý:* Ở lệnh này, chị sẽ thấy hoàn toàn **không có cờ `-p 5432:5432**`. Vì nó dùng chung mạng máy thật, khi Database mở cổng 5432 bên trong, thì tự động máy tính thật của chị cũng mở cổng 5432.

Chị dùng lệnh soi cổng máy thật (đã học Ngày 1) để kiểm chứng:

> `ss -tulpn | grep 5432`
> *(Chị sẽ thấy tiến trình đang giữ cổng này, trực diện và không qua ảo hóa).*
> Xóa con DB đi cho gọn máy: `docker rm -f db-fast`

**Test 3: Mạng Bridge Tùy chỉnh (VPC thu nhỏ)**
Đây là cách làm chuẩn mực nhất để App và DB nhận mặt nhau.

> **📊 Sơ đồ thực hành — Tạo VPC thu nhỏ cho App gọi DB bằng tên:**

```mermaid
flowchart TB
    subgraph step_by_step["🧪 THỰC HÀNH TỪNG BƯỚC"]
        direction TB
        
        S1["<b>Bước 1:</b> Tạo mạng LAN riêng<br/><code>docker network create my_vpc</code>"]
        
        subgraph vpc["🌉 Mạng my_vpc — Subnet 172.19.0.0/16"]
            S2_DB["<b>Bước 2:</b> Ném DB vào mạng<br/><code>docker run --name db-core<br/>--network my_vpc ...</code><br/>🐘 PostgreSQL<br/>IP tự cấp: 172.19.0.2"]
            
            S3_APP["<b>Bước 3:</b> App vào cùng mạng<br/><code>docker run --network my_vpc<br/>alpine ping db-core</code><br/>📦 Alpine Linux<br/>IP tự cấp: 172.19.0.3"]
            
            DNS["🗂️ Docker DNS tự động<br/>'db-core' → 172.19.0.2"]
        end

        subgraph result["📋 KẾT QUẢ"]
            PING["<code>PING db-core (172.19.0.2):<br/>64 bytes from 172.19.0.2<br/>time=0.089 ms ✅</code>"]
            EXPLAIN["🎯 App KHÔNG CẦN biết IP<br/>Chỉ cần biết TÊN 'db-core'<br/>Docker DNS lo phần còn lại!"]
        end
    end

    S1 --> S2_DB
    S1 --> S3_APP
    S3_APP -->|"ping db-core"| DNS
    DNS -->|"→ 172.19.0.2"| S2_DB
    S2_DB -.-> PING
    PING --> EXPLAIN

    style vpc fill:#E3F2FD,stroke:#1565C0,stroke-width:2px
    style result fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
    style S1 fill:#F3E5F5,stroke:#6A1B9A
    style S2_DB fill:#BBDEFB,stroke:#0D47A1
    style S3_APP fill:#BBDEFB,stroke:#0D47A1
    style DNS fill:#FFF9C4,stroke:#F9A825
    style PING fill:#C8E6C9,stroke:#1B5E20
    style EXPLAIN fill:#A5D6A7,stroke:#1B5E20
```

> 💡 **Đây là nền tảng cho Docker Compose:** Sau này trong file `docker-compose.yml`, tất cả service sẽ tự động được ném vào chung 1 Bridge Network và gọi nhau bằng tên!

Tạo một mạng LAN riêng biệt:

> `docker network create my_vpc`

Ném Database vào cái LAN đó:

> `docker run --name db-core --network my_vpc -e POSTGRES_PASSWORD=sieumat -d postgres:15`

Đóng vai trò một con App, chui vào cùng mạng LAN và ping thử vào cái tên `db-core`:

> `docker run -it --rm --network my_vpc alpine ping db-core`
> *(Nó sẽ phân giải tên `db-core` thành IP ảo dạng 172.x.x.x và ping thành công. Ấn `Ctrl+C` dừng lại và gõ `exit` để thoát).*
> Xóa DB đi cho sạch: `docker rm -f db-core`

---

Việc nắm rõ khi nào dùng Bridge, khi nào ép bằng Host, và khi nào cách ly bằng None chính là tư duy kiến trúc của Kỹ sư Hệ thống.

Đến đây, chị đã phải tự tay gõ quá nhiều tham số: `-e`, `-v`, `-p`, `--network`, `--name`... Rất dễ gõ sai chính tả. Chị đã sẵn sàng để "từ bỏ" việc gõ từng dòng lệnh dài ngoằng này, và chuyển sang nhét toàn bộ thông số hạ tầng vào một file văn bản rõ ràng, cấu trúc đẹp đẽ với **Docker Compose** chưa?