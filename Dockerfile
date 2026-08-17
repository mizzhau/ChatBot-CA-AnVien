FROM python:3.11-slim

# Tạo user không phải root theo chuẩn bảo mật của HuggingFace Spaces
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy và cài đặt requirements
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt gunicorn

# Copy toàn bộ source code và database vectorstore
COPY --chown=user . .

# HuggingFace Spaces lắng nghe trên cổng 7860
ENV PORT=7860
EXPOSE 7860

# Chạy ứng dụng bằng gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--timeout", "180", "--workers", "1", "app.app:app"]
