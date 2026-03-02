Chào chị. Hôm nay ta sẽ nói về Storage trong Kubernetes — làm sao để giữ dữ liệu của Database sống sót khi Pod bị xóa.

---

## Ngày 9 - Buổi 1: PersistentVolume (PV) & PersistentVolumeClaim (PVC)

### 1. Ý tưởng cơ bản

Pod ephemeral, nhưng dữ liệu DB thì không. Kubernetes tách trách nhiệm:
- PersistentVolume (PV): tài nguyên lưu trữ trong cluster (nếu cloud thì provisioner tạo đĩa thật, nếu local thì HostPath).
- PersistentVolumeClaim (PVC): Pod yêu cầu 1 lượng storage với class, size và accessMode.

PVC giống như một "Yêu cầu thuê két sắt", PV giống như "két sắt" thật. PVC bind vào PV phù hợp.

### 2. Ví dụ HostPath (lab) — KHÔNG DÙNG trên production

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-hostpath
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /mnt/data/postgres
```

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-postgres
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

Pod sử dụng PVC:

```yaml
spec:
  containers:
  - name: postgres
    image: postgres:15
    volumeMounts:
    - name: pgdata
      mountPath: /var/lib/postgresql/data
  volumes:
  - name: pgdata
    persistentVolumeClaim:
      claimName: pvc-postgres
```

### 3. StorageClass & dynamic provisioning

Trên cloud, dùng `StorageClass` để tự động provision PV khi PVC được tạo. Chị có thể đặt `reclaimPolicy: Retain` để giữ PV sau khi PVC xóa (an toàn dữ liệu).

### 4. StatefulSet vs Deployment cho DB

StatefulSet dùng cho stateful apps: mỗi Pod có tên cố định (stable network ID) và PVC riêng. Thích hợp cho Postgres, Cassandra.

---

**Câu hỏi tư duy:** Nếu chị xóa Pod Postgres, dữ liệu vẫn còn không? (Gợi ý: phụ thuộc vào PVC/PV và reclaimPolicy.)