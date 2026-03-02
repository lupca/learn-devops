Chào chị. Khi cluster lớn hơn 1 người dùng, chị cần phân vùng tài nguyên và đặt giới hạn để tránh "ăn hết đồ chung". Hôm nay ta học Namespace, ResourceQuota và LimitRange.

---

## Ngày 10 - Buổi 1: Namespace & Resource Quota — Phân vùng & giới hạn

### 1. Namespace — phân vùng logic trong cluster

Namespace giống như schema trong DB hoặc một phân vùng tenant: tách các tài nguyên (Pod, Service, PVC) theo tên không gian. Mặc định có `default`, `kube-system`, `kube-public`.

Tạo namespace:

```bash
kubectl create namespace team-a
kubectl get ns
```

Khi apply manifest, chỉ định `metadata.namespace: team-a`.

### 2. ResourceQuota — giới hạn tổng tài nguyên cho namespace

ResourceQuota giới hạn tổng CPU/memory/storage cho toàn bộ namespace.

Ví dụ:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: quota-team-a
  namespace: team-a
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    persistentvolumeclaims: "5"
```

Khi vượt quota, Pod sẽ không được tạo.

### 3. LimitRange — giới hạn mặc định cho từng Pod/Container

LimitRange giúp đặt `requests` và `limits` mặc định cho CPU/MEM nếu developer quên cấu hình. Giúp scheduler có thông tin tốt hơn.

Ví dụ limitrange:

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: limits
  namespace: team-a
spec:
  limits:
  - default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 250m
      memory: 256Mi
    type: Container
```

### 4. Multi-tenant considerations

- Dùng namespace + RBAC + NetworkPolicy để cô lập.
- ResourceQuota bảo vệ cluster khỏi "noisy neighbor".

---

**Câu hỏi tư duy:** Nếu một developer deploy nhiều Pod mà không đặt `resources.requests`, scheduler có thể đặt Pod đó lên node không đủ tài nguyên gây OOMKill hoặc noisy neighbor. Làm sao để ngăn điều này ở cấp team?