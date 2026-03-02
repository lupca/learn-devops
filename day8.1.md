Chào chị. Hôm nay chúng ta sẽ học thứ khiến K8s trở nên "thông minh": Deployment và ReplicaSet — đảm bảo số bản sao (replicas) luôn đúng, tự động cập nhật và tự chữa bệnh khi có node/Pod bị lỗi.

---

## Ngày 8 - Buổi 1: Deployment & ReplicaSet — Đảm bảo luôn có N bản sao chạy

### 1. ReplicaSet — giữ N bản sao luôn chạy

ReplicaSet (RS) là tài nguyên đảm bảo có đúng số bản sao Pod.

- Nếu 1 Pod chết, RS ngay lập tức tạo Pod mới.
- RS không biết cách nâng cấp; đó là việc của Deployment.

### 2. Deployment — quản lý vòng đời (rolling update, rollback)

Deployment tạo và quản lý ReplicaSet. Khi chị cập nhật image mới, Deployment tạo RS mới, thực hiện rolling update theo chiến lược chị cấu hình (rolling, recreate), và cho phép rollback nếu có lỗi.

### 3. Ví dụ YAML: Deployment 3 replicas (nginx)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deploy
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
        image: nginx:1.24-alpine
        ports:
        - containerPort: 80
```

Apply và quan sát:

```bash
kubectl apply -f web-deploy.yaml
kubectl get deployments
kubectl get rs
kubectl get pods -l app=web
```

### 4. Rolling update & zero-downtime

Khi đổi image (ví dụ `nginx:1.24-alpine` → `nginx:1.25`), chị có thể dùng:

```bash
kubectl set image deployment/web-deploy nginx=nginx:1.25 --record
kubectl rollout status deployment/web-deploy

# Nếu có lỗi:
kubectl rollout undo deployment/web-deploy
```

Deployment mặc định thực hiện rolling update: tắt từng Pod cũ sau khi Pod mới đã sẵn sàng — đảm bảo không downtime.

### 5. Self-healing & liveness/readiness probes

- Readiness probe: thông báo Pod đã sẵn sàng nhận traffic (tương tự healthcheck ở Compose).
- Liveness probe: nếu Pod bị treo, kubelet sẽ restart container.

Ví dụ probes trong spec:

```yaml
readinessProbe:
  httpGet:
    path: /healthz
    port: 80
  initialDelaySeconds: 5
  periodSeconds: 10

livenessProbe:
  httpGet:
    path: /live
    port: 80
  initialDelaySeconds: 15
  periodSeconds: 20
```

---

**Câu hỏi tư duy:** Nếu chị muốn đảm bảo luôn có 5 Pod nhưng muốn tối đa 2 Pod mới được tạo cùng lúc khi rolling update, và tối thiểu giữ 3 Pod trong suốt quá trình update, chị sẽ cấu hình `maxUnavailable` và `maxSurge` như thế nào trong `strategy` của Deployment?