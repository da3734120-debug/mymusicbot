FROM python:3.11-slim

# ដំឡើង FFmpeg, libopus និងឧបករណ៍សម្រាប់ជួយបង្កើតកូដប្រព័ន្ធសម្ងាត់ DAVE ថ្មី
RUN apt-get update && \
    apt-get install -y ffmpeg libopus-dev build-essential curl pkg-config git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
