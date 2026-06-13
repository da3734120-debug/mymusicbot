FROM python:3.11-slim

# ដំឡើងកម្មវិធីចាក់ភ្លេង FFmpeg និងបណ្ណាល័យសំឡេង Opus ផ្លូវការចូលក្នុងប្រព័ន្ធ Linux
RUN apt-get update && \
    apt-get install -y ffmpeg libopus-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ដំណើរការ Bot ភ្លេង
CMD ["python", "main.py"]
