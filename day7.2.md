Chào chị. Bây giờ chị đã biết K8s là gì — giờ ta sẽ dựng một cụm nhẹ nhàng và đẻ Pod đầu tiên. Ta dùng `k3s` (nhẹ, production-ready) hoặc `kind`/`minikube` nếu chị muốn chạy trên máy cá nhân.

---

## Ngày 7 - Buổi 2: Cài k3s (nhanh) và Triệu hồi Pod đầu tiên

### 1. Lựa chọn môi trường thử nghiệm

- k3s: nhẹ, dễ cài trên VM hoặc máy thật. Tốt cho lab và production nhỏ.
- minikube: chạy K8s trong 1 VM trên laptop.
- kind: chạy K8s trong Docker (chạy local cluster bằng Docker).

Ở đây tôi sẽ hướng dẫn nhanh k3s (1 lệnh). Nếu chị dùng macOS có `brew`, hoặc dùng Linux trên VM đều OK.

### 2. Cài k3s (1 node cluster)

Trên một máy (VM) gõ:

```bash
# Cài k3s (chạy dưới quyền root hoặc sudo)
curl -sfL https://get.k3s.io | sh -

# Kiểm tra node
sudo k3s kubectl get nodes
```

K3s cài xong sẽ tự động chạy control plane + worker trên cùng máy (single-node), và `kubectl` được đóng gói sẵn (thông qua `k3s kubectl`).

### 3. Triệu hồi Pod đầu tiên

Tạo một Pod chạy nginx bằng lệnh nhanh:

```bash
# Dùng kubectl (k3s kubectl trên k3s)
kubectl run web-demo --image=nginx:alpine --port=80 --restart=Never

# Kiểm tra Pod
kubectl get pods

# Xem log
kubectl logs web-demo
```

Hoặc tạo bằng manifest YAML (khuyến khích):

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-demo
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80
```

Apply:

```bash
kubectl apply -f pod-web.yaml
kubectl get pods -o wide
```

### 4. Truy cập Pod (port-forward)

Để truy cập web server trong Pod từ laptop:

```bash
kubectl port-forward pod/web-demo 8080:80
# Mở http://localhost:8080
```

### 5. Mẹo nhỏ & debugging

- `kubectl describe pod web-demo` để xem events (thường hữu ích nếu Pod CrashLoopBackOff).
- `kubectl get events --sort-by=.metadata.creationTimestamp` để đọc lịch sử sự kiện.
- Nếu Pod không pull được image, kiểm tra network/registry hoặc image name.

---

**Câu hỏi tư duy:** Chị vừa tạo Pod bằng `kubectl run` và bằng `kubectl apply -f`. Khi nào chị nên dùng Manifest file thay vì lệnh `run` đơn giản? (Gợi ý: tái sử dụng, version-control, reproducibility).