Chào chị. Hôm nay chúng ta học cách tách cấu hình khỏi code: dùng ConfigMap cho cấu hình công khai, Secret cho bí mật (mật khẩu, token).

---

## Ngày 9 - Buổi 2: ConfigMap & Secret — Tách cấu hình khỏi image

### 1. ConfigMap — cấu hình bình thường

ConfigMap lưu các config không bí mật (file .conf, ENV vars). Có thể mount dưới dạng file hoặc inject vào environment variables.

Ví dụ:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-config
data:
  APP_MODE: "production"
  WELCOME_MSG: "Chào chị, chào mừng đến hệ thống"
```

Trong Pod:

```yaml
envFrom:
- configMapRef:
    name: web-config
```

Hoặc mount file:

```yaml
volumes:
- name: config-volume
  configMap:
    name: web-config
volumeMounts:
- name: config-volume
  mountPath: /etc/app/config
```

### 2. Secret — lưu mật khẩu & token

Secret mã hóa trên etcd (base64 in YAML, nhưng etcd lưu mã hoá). Không push file chứa giá trị secret lên Git.

Tạo secret:

```bash
kubectl create secret generic db-secret \
  --from-literal=POSTGRES_PASSWORD=sieumat123
```

Inject vào Pod:

```yaml
env:
- name: POSTGRES_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-secret
      key: POSTGRES_PASSWORD
```

Hoặc mount secret as file.

### 3. Best practices

- Không lưu secrets minh bạch trong repo.
- Dùng KMS/Vault hoặc SealedSecrets/External Secrets cho production.
- Hạn chế quyền truy cập Secret bằng RBAC.

---

**Câu hỏi tư duy:** Nếu chị cần xoay mật khẩu DB theo tuần, chị sẽ dùng công cụ nào để tự động cập nhật Secret trong cluster mà không phải edit YAML thủ công? (Gợi ý: Vault, External Secrets Operator).