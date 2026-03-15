import sys
import time
import requests
import os

def main():
    if len(sys.argv) < 2:
        print("Lỗi: Yêu cầu truyền vào 1 tham số!")
        print("Sử dụng: python main.py <tham_so>")
        sys.exit(1)

    tham_so = sys.argv[1]
    
    print(f"[OCR module] Bắt đầu xử lý. Tham số đầu vào: '{tham_so}'")
    
    # Kiểm tra file giả lập trong thư mục input
    file_path = os.path.join("input", tham_so)
    if os.path.exists(file_path):
        print(f"[OCR module] Đang xử lý file {file_path} ...")
    else:
        print(f"[OCR module] Cảnh báo: Không tìm thấy file {file_path}. Vẫn tiếp tục xử lý mô phỏng...")

    print("[OCR module] Đang xử lý... (sleep 2s)")
    time.sleep(2)
    print("[OCR module] Xử lý xong!")

    # 2. Gọi tới container azure-DI
    url = os.environ.get("API_URL", "http://localhost:8080/get")
    print(f"\n[OCR module] Thực hiện gọi API tới azure-DI tại {url}...")
    
    try:
   
        response = requests.get(url, params={"input": tham_so}, timeout=5)
        response.raise_for_status()
        
  
        data = response.json()
        print("[OCR module] Gọi API thành công!")
        print("-" * 40)
        print("KẾT QUẢ TỪ AZURE-DI:")
        print(f"  URL được gọi: {data.get('url')}")
        print(f"  Tham số gửi đi (args): {data.get('args')}")
        print(f"  Origin IP: {data.get('origin')}")
        print("-" * 40)
        

        return data
        
    except requests.exceptions.RequestException as e:
        print(f"[OCR module] Lỗi khi gọi azure-DI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    result = main()
    
