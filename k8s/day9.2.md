## Ngày 9 - Buổi 2: ConfigMap & Secret — Tách cấu hình ra khỏi code

Buổi trước chị hardcode mật khẩu PostgreSQL trong file YAML. Đây là **sai lầm nghiêm trọng** trong production: push YAML lên Git = lộ mật khẩu. Hôm nay chị sẽ học cách tách cấu hình và bí mật ra khỏi code, quản lý chúng đúng cách.

---

### 1. Vấn đề: Hardcode cấu hình = Thảm họa

```yaml
# ❌ TUYỆT ĐỐI KHÔNG LÀM THẾ NÀY trong production
env:
  - name: POSTGRES_PASSWORD
    value: "SuperSecret123!"      # Lộ trên Git!
  - name: DATABASE_URL
    value: "postgres://user:pass@host:5432/db"
  - name: REDIS_HOST
    value: "redis.internal"       # Đổi mỗi môi trường
```

**3 vấn đề:**
1. **Bảo mật:** Mật khẩu nằm trong Git → ai cũng đọc được.
2. **Linh hoạt:** Mỗi môi trường (dev/staging/prod) cấu hình khác nhau → phải sửa YAML.
3. **Phân quyền:** Developer cần biết port DB, nhưng KHÔNG cần biết mật khẩu.

> 💡 **Góc nhìn Database:** Giống việc viết mật khẩu thẳng trong `pg_hba.conf` dạng plaintext vs dùng `.pgpass` file riêng. Nguyên tắc: **Tách credential ra khỏi config chính**.

---

### 2. ConfigMap — Cấu hình KHÔNG bí mật

ConfigMap lưu cấu hình thường (port, hostname, feature flags...) dưới dạng key-value.

```mermaid
flowchart LR
    CM["📋 ConfigMap<br/><i>app-config</i><br/><br/>DB_HOST=postgres-svc<br/>DB_PORT=5432<br/>DB_NAME=myapp<br/>LOG_LEVEL=info"]
    
    P1["🟢 Pod Web #1"]
    P2["🟢 Pod Web #2"]
    P3["🟢 Pod Web #3"]

    CM -->|"inject env"| P1
    CM -->|"inject env"| P2
    CM -->|"inject env"| P3

    style CM fill:#E3F2FD,stroke:#1565C0,stroke-width:2px
```

#### Cách 1: Tạo ConfigMap bằng YAML

```yaml
# configmap-app.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DB_HOST: "postgres-service"
  DB_PORT: "5432"
  DB_NAME: "myapp"
  LOG_LEVEL: "info"
  APP_ENV: "development"
```

```bash
kubectl apply -f configmap-app.yaml
kubectl get configmap
kubectl describe configmap app-config
```

#### Cách 2: Tạo ConfigMap bằng lệnh

```bash
kubectl create configmap app-config \
  --from-literal=DB_HOST=postgres-service \
  --from-literal=DB_PORT=5432 \
  --from-literal=LOG_LEVEL=info
```

#### Cách 3: Tạo ConfigMap từ file cấu hình

```bash
# Tạo file nginx.conf
cat <<'EOF' > custom-nginx.conf
server {
    listen 80;
    server_name myapp.local;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
    }
    
    location /api {
        proxy_pass http://api-service:3000;
    }
}
EOF

kubectl create configmap nginx-config --from-file=custom-nginx.conf
kubectl describe configmap nginx-config
```

---

### 3. Inject ConfigMap vào Pod (3 cách)

#### Cách A: Inject từng key → biến môi trường

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: app
          image: nginx:1.25
          env:
            - name: DATABASE_HOST       # Tên biến trong Container
              valueFrom:
                configMapKeyRef:
                  name: app-config      # Tên ConfigMap
                  key: DB_HOST          # Key trong ConfigMap
            - name: DATABASE_PORT
              valueFrom:
                configMapKeyRef:
                  name: app-config
                  key: DB_PORT
```

#### Cách B: Inject TẤT CẢ key cùng lúc

```yaml
spec:
  containers:
    - name: app
      image: nginx:1.25
      envFrom:                       # Inject toàn bộ ConfigMap
        - configMapRef:
            name: app-config
      # Bây giờ Container có: DB_HOST, DB_PORT, DB_NAME, LOG_LEVEL, APP_ENV
```

#### Cách C: Mount ConfigMap thành file (dùng cho config file)

```yaml
spec:
  containers:
    - name: nginx
      image: nginx:1.25
      volumeMounts:
        - name: nginx-conf
          mountPath: /etc/nginx/conf.d   # Mount vào thư mục config
      volumes:
        - name: nginx-conf
          configMap:
            name: nginx-config           # ConfigMap chứa nginx.conf
```

> **📊 So sánh 3 cách inject:**

```mermaid
flowchart TB
    CM["📋 ConfigMap"]
    
    subgraph envA["Cách A: Từng key"]
        EA["env:\n  - name: DB_HOST\n    valueFrom:\n      configMapKeyRef"]
    end
    
    subgraph envB["Cách B: Tất cả key"]
        EB["envFrom:\n  - configMapRef:\n      name: app-config"]
    end
    
    subgraph volC["Cách C: Mount file"]
        EC["volumeMounts:\n  mountPath: /etc/nginx/conf.d"]
    end

    CM --> envA
    CM --> envB
    CM --> volC

    style envA fill:#E3F2FD,stroke:#1565C0
    style envB fill:#E8F5E9,stroke:#2E7D32
    style volC fill:#FFF3E0,stroke:#E65100
```

---

### 4. Secret — Cho dữ liệu BÍ MẬT

Secret giống ConfigMap nhưng:
- Giá trị được **mã hóa Base64** (không phải encryption, chỉ là encoding).
- Được lưu **mã hóa trên etcd** (nếu bật EncryptionConfiguration).
- Có thể phân quyền RBAC: chỉ admin mới đọc Secret.

#### Tạo Secret bằng lệnh (cách khuyên dùng)

```bash
kubectl create secret generic db-credentials \
  --from-literal=POSTGRES_USER=admin \
  --from-literal=POSTGRES_PASSWORD='SuperSecret123!' \
  --from-literal=DATABASE_URL='postgres://admin:SuperSecret123!@postgres-service:5432/myapp'
```

```bash
kubectl get secrets
kubectl describe secret db-credentials
```

```
Name:         db-credentials
Data
====
POSTGRES_USER:     5 bytes
POSTGRES_PASSWORD: 16 bytes
DATABASE_URL:      65 bytes
```

> 🧐 Lưu ý: `kubectl describe` **không hiển thị giá trị** Secret. Để xem:
```bash
kubectl get secret db-credentials -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d
# → SuperSecret123!
```

#### Tạo Secret bằng YAML

```yaml
# secret-db.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
stringData:                 # stringData = tự encode Base64
  POSTGRES_USER: admin
  POSTGRES_PASSWORD: "SuperSecret123!"
```

> ⚠️ **CẢNH BÁO:** File YAML chứa Secret **TUYỆT ĐỐI KHÔNG push lên Git**. Dùng lệnh `kubectl create secret` hoặc tool như **Sealed Secrets / External Secrets Operator** trong production.

---

### 5. Inject Secret vào Pod

```yaml
# postgres-with-secret.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:           # Lấy từ Secret (không phải ConfigMap!)
                  name: db-credentials
                  key: POSTGRES_USER
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: POSTGRES_PASSWORD
            - name: POSTGRES_DB         # Cấu hình thường → dùng ConfigMap
              valueFrom:
                configMapKeyRef:
                  name: app-config
                  key: DB_NAME
          volumeMounts:
            - name: pg-data
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: pg-data
          persistentVolumeClaim:
            claimName: postgres-data
```

```bash
kubectl apply -f postgres-with-secret.yaml
kubectl get pods -w   # Đợi Running

# Kiểm tra: biến môi trường có đúng không?
kubectl exec -it deploy/postgres -- env | grep POSTGRES
# POSTGRES_USER=admin
# POSTGRES_PASSWORD=SuperSecret123!
# POSTGRES_DB=myapp
```

---

### 6. Lab tổng hợp: Web App + PostgreSQL (chuẩn production)

```yaml
# full-app.yaml

# --- ConfigMap ---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DB_HOST: "postgres-service"
  DB_PORT: "5432"
  DB_NAME: "myapp"
  APP_ENV: "development"
---
# --- PVC cho PostgreSQL ---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 1Gi
---
# --- PostgreSQL Deployment ---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: POSTGRES_USER
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: POSTGRES_PASSWORD
            - name: POSTGRES_DB
              valueFrom:
                configMapKeyRef:
                  name: app-config
                  key: DB_NAME
            - name: PGDATA
              value: "/var/lib/postgresql/data/pgdata"
          volumeMounts:
            - name: pg-data
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: pg-data
          persistentVolumeClaim:
            claimName: postgres-data
---
# --- PostgreSQL Service ---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  type: ClusterIP
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
---
# --- Web App Deployment ---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx:1.25
          ports:
            - containerPort: 80
          envFrom:
            - configMapRef:
                name: app-config
---
# --- Web Service ---
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080
```

```bash
# Tạo Secret trước (vì YAML không nên chứa Secret)
kubectl create secret generic db-credentials \
  --from-literal=POSTGRES_USER=admin \
  --from-literal=POSTGRES_PASSWORD='SuperSecret123!'

# Áp dụng toàn bộ
kubectl apply -f full-app.yaml

# Kiểm tra
kubectl get all
kubectl get configmap
kubectl get secret
kubectl get pvc
```

---

### 7. Best Practices — Quy tắc vàng

| Quy tắc | ❌ Sai | ✅ Đúng |
| --- | --- | --- |
| Mật khẩu | Hardcode trong YAML | Secret + `secretKeyRef` |
| Cấu hình | Hardcode trong Dockerfile | ConfigMap + `envFrom` |
| Secret file | Push YAML Secret lên Git | `kubectl create secret` bằng lệnh |
| Production Secret | K8s Secret thường | Sealed Secrets / Vault |
| Phân môi trường | 1 file cho tất cả | ConfigMap/Secret riêng cho dev/staging/prod |

---

### 8. Dọn dẹp

```bash
kubectl delete -f full-app.yaml 2>/dev/null
kubectl delete secret db-credentials
kubectl delete pvc postgres-data
kubectl delete configmap app-config nginx-config 2>/dev/null
```

---

### ✅ Checklist cuối buổi

| Kỹ năng | Lệnh | ✅ |
| --- | --- | --- |
| Tạo ConfigMap | `kubectl create configmap` | ☐ |
| Inject ConfigMap (env) | `envFrom` hoặc `configMapKeyRef` | ☐ |
| Mount ConfigMap (file) | `volumeMounts` + `configMap` | ☐ |
| Tạo Secret | `kubectl create secret generic` | ☐ |
| Inject Secret | `secretKeyRef` | ☐ |
| Không push Secret lên Git | YAML Secret → `.gitignore` | ☐ |

---

**Câu hỏi tư duy cuối buổi:**
Chị có 2 team: **team-web** và **team-data**. Cả 2 đều deploy trên cùng 1 cluster K8s. Làm sao để đảm bảo:
1. Pod của team-web không thấy Pod của team-data (cách ly).
2. Team-data không dùng hết RAM/CPU của cluster (giới hạn tài nguyên).

(Gợi ý: **Namespace** + **ResourceQuota**)

Buổi sau: **Namespace & Resource Management** — Phân vùng cluster cho nhiều team.
