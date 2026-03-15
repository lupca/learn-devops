# 🎯 Bài Tập: Xây Dựng Hệ Thống Polling & Tích Hợp API (Dockerized)

**📌 Tình huống thực tế:**
Trong các hệ thống lớn, các thành phần thường được thiết kế rời rạc: một module điều phối dò tìm công việc mới (Polling), một module xử lý nhận dạng (OCR), và một module gọi API (DI). Các thành phần giao tiếp qua chung một vùng nhớ (Volume) và mạng ảo (Network).

**Mục tiêu bài tập:**
Em hãy container hóa cấu hình thành phần hệ thống hiện tại và xây dựng một luồng làm việc tự động với các yêu cầu sau:

### Yêu cầu 1: Ứng dụng Polling (Điều phối tự động)
- **Tạo một ứng dụng Polling (Script bash hoặc python):**
  - Giả lập việc gọi cơ sở dữ liệu (DB).
  - Dữ liệu trả về từ DB chứa một trường `file_name` (Ví dụ: `hoadon_01.jpg`).
- **Kích hoạt module OCR (`main.py`):**
  - Polling script tự động gọi module OCR bằng dòng lệnh, truyền `file_name` làm đối số (Ví dụ: `python main.py hoadon_01.jpg`). Sau khi module OCR được khởi chạy, script Polling hiện tại kết thúc quá trình.
- **Tự động hóa bằng Crontab:**
  - Cấu hình **crontab** bên trong Docker Container để chạy script Polling này **tự động mỗi 10 giây 1 lần**.

### Yêu cầu 2: Quản lý Thư Mục Dùng Chung (Volume)
- **Dữ liệu mồi (Input):**
  - Tạo sẵn một thư mục tên là `input` ở cùng thư mục dự án trên máy host và tạo sẵn 1 vài file trống (ví dụ `hoadon_01.jpg`) bên trong.
- **Cấu hình Shared Volume (Mount thư mục):**
  - Trong cấu hình sinh ra container, hãy mount thư mục `input` từ máy host vào bên trong container chứa OCR/Polling. Module OCR (`main.py`) đã được viết sẵn chức năng tự động vào điểm mount `input` để đọc file. Cần đảm bảo volume truyền vào chính xác để OCR có thể nhận diện được file.

### Yêu cầu 3: Container hóa & Thiết lập Mạng (Docker Networking)
- **Đóng gói bằng Docker:** Container hóa toàn bộ các ứng dụng trên. 
- **Kết nối thông nhau:**
  - Triển khai container gọi API tên là `azure-DI` (sử dụng image `kennethreitz/httpbin`).
  - Yêu cầu ứng dụng OCR và module DI phải được **thông mạng** với nhau (cùng một network) để module OCR có thể gọi API tới container DI. Em có thể truyền URL phù hợp bằng Environment Variable (như `API_URL`) vào container chạy module OCR cho nó gọi tới dịch vụ API.
