Chào chị. Sau khi đã có Pod và Deployment, bước tiếp theo là làm cho các Pod đó có thể nghe được từ bên trong Cluster và (khi cần) từ bên ngoài: đó là phần Networking của Kubernetes — Service và Ingress.

---

## Ngày 8 - Buổi 2: Service & Networking — Kết nối Pod với thế giới

### 1. Service — cách Kubernetes expose Pod

Pod là ephemeral (tạo/xóa). Service cung cấp một endpoint ổn định (ClusterIP) cho các Pod thay đổi phía sau.

Các loại Service:
- ClusterIP (mặc định): chỉ trong cluster, dùng cho internal communication.
- NodePort: mở port trên mỗi Node để truy cập từ bên ngoài (hostIP:nodePort)
- LoadBalancer: cloud provider cung cấp LB và ánh xạ tới service (thường dùng trên cloud)
- Headless Service (clusterIP: None): trả về IP Pod trực tiếp, dùng cho stateful apps / service discovery

### 2. Ví dụ Service (ClusterIP)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-svc
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

`kubectl apply -f web-svc.yaml` → `kubectl get svc web-svc`

### 3. NodePort & LoadBalancer

- NodePort: dễ thử nghiệm trên cluster local. Kubernetes chọn port ngẫu nhiên trong dải (30000-32767) hoặc chị chỉ định.
- LoadBalancer: trên cloud sẽ tạo 1 LB (ELB/ALB) và ánh xạ tới NodePort.

### 4. Ingress — L7 routing cho HTTP

Ingress là điểm vào L7: cho phép rule theo host/path, TLS termination, rewrite path.

Ví dụ Ingress rule:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
spec:
  rules:
  - host: example.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-svc
            port:
              number: 80
```

Lưu ý: cần 1 Ingress Controller (nginx-ingress, traefik) chạy trong cluster để Ingress hoạt động.

### 5. Service Discovery & DNS

K8s có DNS nội bộ (CoreDNS). Service `web-svc` có DNS dạng `web-svc.default.svc.cluster.local` — Pod khác có thể `curl http://web-svc` trực tiếp.

### 6. Mẹo vận hành

- Dùng Service + Readiness probe để kube-proxy chỉ route tới Pod đã sẵn sàng.
- Trên Minikube/local, test NodePort bằng `minikube service web-svc --url`.
- Nếu deploy trên bare-metal, cân nhắc MetalLB để có LoadBalancer.

---

**Câu hỏi tư duy:** Khi nào nên dùng Ingress (L7) thay vì LoadBalancer (L4)? Đáp án ngắn: Khi chị cần routing theo host/path, TLS termination, hoặc rewrite URL — Ingress là lựa chọn phù hợp.