# Sử dụng image Python chính thức
FROM python:3.9-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép requirements.txt vào container
COPY requirements.txt /app/

# Cập nhật pip và cài đặt các công cụ cần thiết
RUN pip install --upgrade pip setuptools wheel

# Cài đặt các thư viện từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn vào container
COPY . /app/

# Lệnh để chạy ứng dụng
CMD ["python", "main.py"]
