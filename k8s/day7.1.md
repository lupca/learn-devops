Chào chị. Docker Compose chỉ huy được một tiểu đội Container trên **1 máy**. Nhưng trong thực tế doanh nghiệp, hệ thống cần chạy trên **nhiều máy chủ**, cần tự động phục hồi khi Server sập, cần nâng cấp phần mềm mà người dùng không hề biết. Docker Compose không làm được những điều đó.

Giải pháp: **Kubernetes (K8s)** — Tổng Tư Lệnh điều phối Container trên quy mô lớn. Hãy tưởng tượng Docker Compose là quản lý 1 nhà hàng, thì K8s là quản lý cả chuỗi 100 nhà hàng trên toàn quốc.

---

## Ngày 7 - Buổi 1: Giải mã Kubernetes — Từ "1 máy" lên "cả đế chế"

### 1. Tại sao cần K8s? (Câu chuyện thực tế)

Chị tưởng tượng hệ thống công ty đang chạy trên Docker Compose:

- **Thứ Hai:** Mọi thứ chạy ngon trên 1 Server.
- **Thứ Ba:** Lượng khách tăng gấp 10 lần. 1 Server không chịu nổi. Chị muốn chạy thêm 5 bản sao Web App trên 5 máy khác nhau → Docker Compose **không biết cách** phân tán Container sang máy khác.
- **Thứ Tư:** Server chứa DB bị hỏng ổ cứng lúc 3 giờ sáng. Docker có `restart: always` nhưng nếu **cả máy chết** thì ai đẻ lại Container trên máy khác? → Docker Compose **bó tay**.
- **Thứ Năm:** Sếp yêu cầu nâng cấp Web App lên version mới mà người dùng không được bị gián đoạn → Docker Compose **không hỗ trợ** rolling update tự động.

Kubernetes giải quyết **tất cả** những vấn đề trên.

> **📊 Sơ đồ so sánh Docker Compose vs Kubernetes:**

```mermaid
flowchart LR
    subgraph compose["🐳 Docker Compose"]
        direction TB
        C_SCOPE["📍 Phạm vi: 1 máy duy nhất"]
        C_SCALE["📈 Scale: Chỉ tăng Container trên 1 máy"]
        C_HEAL["🩹 Self-heal: Restart Container<br/>❌ Máy chết = Hết cách"]
        C_UPDATE["🔄 Update: Phải tắt → bật lại<br/>❌ Có downtime"]
    end

    subgraph k8s["☸️ Kubernetes"]
        direction TB
        K_SCOPE["📍 Phạm vi: NHIỀU máy (Cluster)"]
        K_SCALE["📈 Scale: Tự phân tán Pod sang máy khác"]
        K_HEAL["🩹 Self-heal: Máy chết → K8s đẻ Pod<br/>lên máy khác trong vài giây"]
        K_UPDATE["🔄 Update: Rolling update<br/>✅ Zero-downtime"]
    end

    style compose fill:#FFF3E0,stroke:#E65100,stroke-width:2px
    style k8s fill:#E3F2FD,stroke:#1565C0,stroke-width:2px
```

> 💡 **Một câu ghi nhớ:** Docker Compose = Quản lý 1 quán cafe. Kubernetes = Quản lý chuỗi 100 quán cafe toàn quốc, tự mở quán mới khi quán nào bị cháy.

---

### 2. Kiến trúc Kubernetes (Giải thích từng thành phần)

Một cụm K8s (Cluster) gồm 2 loại máy:

**🏛️ Control Plane (Ban Giám đốc)** — Bộ não ra quyết định, không chạy ứng dụng:

| Thành phần | Vai trò (Góc nhìn Database) | Giải thích |
| --- | --- | --- |
| **API Server** | **Cổng tiếp nhận lệnh** (giống cổng `psql`) | Mọi lệnh `kubectl` đều gửi tới đây. Là cửa duy nhất vào hệ thống. |
| **etcd** | **System Catalog / WAL Log** | Cơ sở dữ liệu key-value lưu TOÀN BỘ trạng thái cluster. Mất etcd = mất cluster. |
| **Scheduler** | **Query Optimizer** | Quyết định Pod chạy trên Node nào (giống Optimizer chọn execution plan). |
| **Controller Manager** | **Trigger / Stored Procedure tự động** | Liên tục kiểm tra: "Đang có 2 Pod, cần 3 → đẻ thêm 1". Hoạt động như trigger tự động. |

**🏗️ Worker Node (Nhân viên)** — Máy chủ chạy ứng dụng thật:

| Thành phần | Vai trò (Góc nhìn Database) | Giải thích |
| --- | --- | --- |
| **kubelet** | **Agent giám sát** | Chạy trên mỗi Node, nhận lệnh từ API Server và đảm bảo Container chạy đúng. |
| **kube-proxy** | **Connection Pooler (PgBouncer)** | Quản lý luật mạng, điều phối traffic từ Service tới đúng Pod. |
| **Container Runtime** | **Database Engine** | Phần mềm chạy Container (containerd). Giống PostgreSQL Engine thực thi query. |

> **📊 Sơ đồ kiến trúc Kubernetes Cluster:**

```mermaid
graph TB
    subgraph cp["🏛️ CONTROL PLANE (Ban Giám đốc)"]
        direction LR
        API["🚪 API Server<br/><i>Cổng tiếp nhận mọi lệnh</i>"]
        ETCD["💾 etcd<br/><i>Bộ nhớ trạng thái<br/>(System Catalog)</i>"]
        SCHED["🧠 Scheduler<br/><i>Chọn Node cho Pod<br/>(Query Optimizer)</i>"]
        CM["⚙️ Controller Manager<br/><i>Đảm bảo đúng số Pod<br/>(Auto Trigger)</i>"]
        API --- ETCD
        API --- SCHED
        API --- CM
    end

    subgraph n1["🖥️ WORKER NODE 1"]
        direction TB
        KL1["kubelet + kube-proxy"]
        subgraph pods1["Pods đang chạy"]
            P1["🐘 Pod: PostgreSQL"]
            P2["🌐 Pod: Web App #1"]
        end
        KL1 --> pods1
    end

    subgraph n2["🖥️ WORKER NODE 2"]
        direction TB
        KL2["kubelet + kube-proxy"]
        subgraph pods2["Pods đang chạy"]
            P3["🌐 Pod: Web App #2"]
            P4["🌐 Pod: Web App #3"]
        end
        KL2 --> pods2
    end

    ADMIN["👤 Chị gõ:<br/><code>kubectl get pods</code>"]
    ADMIN -->|"gửi lệnh"| API
    API -->|"lệnh tới Node"| KL1
    API -->|"lệnh tới Node"| KL2

    style cp fill:#E3F2FD,stroke:#1565C0,stroke-width:2px
    style n1 fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
    style n2 fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
    style ADMIN fill:#FFF9C4,stroke:#F9A825
```

---

### 3. Từ điển K8s dành cho dân Database

| Khái niệm K8s | Tương đương Docker | Góc nhìn Database | Giải thích |
| --- | --- | --- | --- |
| **Pod** | Container | **1 Process DB đang chạy** | Đơn vị nhỏ nhất. 1 Pod thường = 1 Container. |
| **Deployment** | *(không có)* | **Quy trình Backup-Restore tự động** | Đảm bảo luôn có N bản sao Pod. Tự đẻ lại khi chết. |
| **Service** | Port `-p` | **DNS + PgBouncer** | Endpoint ổn định để gọi Pod. Pod chết IP đổi, Service giữ nguyên. |
| **Namespace** | *(không có)* | **Schema** | Phân vùng: production, staging, team-a. |
| **PersistentVolume** | Volume `-v` | **Tablespace** | Dữ liệu bền vững, Pod chết data vẫn còn. |
| **ConfigMap** | Environment vars | **postgresql.conf** | Cấu hình không bí mật. |
| **Secret** | `.env` file | **Mật khẩu pg_hba.conf** | Mật khẩu, token. Mã hóa trên etcd. |
| **Ingress** | *(không có)* | **Reverse Proxy** | Điều hướng HTTP từ ngoài vào Service. |

---

### 4. Vòng đời một Request trong K8s

> **📊 Sơ đồ hành trình request từ người dùng đến Database:**

```mermaid
flowchart LR
    USER["👤 Người dùng<br/>truy cập web"]
    ING["🚪 Ingress<br/>(Cổng vào L7)"]
    SVC["🔗 Service: web<br/>(Load Balance)"]
    
    subgraph nodes["☸️ Kubernetes Cluster"]
        POD1["🌐 Pod Web #1"]
        POD2["🌐 Pod Web #2"]
        POD3["🌐 Pod Web #3"]
        DB_SVC["🔗 Service: postgres"]
        DB_POD["🐘 Pod PostgreSQL"]
        PVC["💾 PersistentVolume<br/>(Data bất tử)"]
    end

    USER --> ING --> SVC
    SVC -->|"Round Robin"| POD1 & POD2 & POD3
    POD1 & POD2 & POD3 -->|"SQL query"| DB_SVC --> DB_POD
    DB_POD --> PVC

    style nodes fill:#F5F5F5,stroke:#424242,stroke-width:2px
    style SVC fill:#BBDEFB,stroke:#0D47A1
    style DB_SVC fill:#BBDEFB,stroke:#0D47A1
    style PVC fill:#FCE4EC,stroke:#C62828
```

---

### 5. `kubectl` — "psql" của Kubernetes

| Lệnh kubectl | Tương đương DB | Ý nghĩa |
| --- | --- | --- |
| `kubectl get pods` | `SELECT * FROM pg_stat_activity` | Xem Pod đang chạy |
| `kubectl get nodes` | Xem danh sách Server | Xem các máy trong cluster |
| `kubectl describe pod <tên>` | `EXPLAIN ANALYZE` | Chi tiết trạng thái + events |
| `kubectl logs <tên>` | Xem `pg_log` | Đọc nhật ký Pod |
| `kubectl exec -it <tên> -- bash` | `psql` | Chui vào bên trong Pod |
| `kubectl apply -f file.yaml` | `psql -f migration.sql` | Áp dụng cấu hình từ file |
| `kubectl delete pod <tên>` | `pg_terminate_backend()` | Giết 1 Pod |

---

**Câu hỏi tư duy cuối buổi:**
Docker Compose cũng có `restart: always` để tự khởi động lại Container. Vậy tại sao K8s vẫn cần thiết? (Gợi ý: `restart` chỉ hoạt động khi **máy còn sống**. Nếu **cả máy chết** thì sao?)

Buổi sau chúng ta sẽ **tự tay dựng Cluster K8s** trên máy chị và triệu hồi Pod đầu tiên!
