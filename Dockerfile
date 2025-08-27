FROM python:3.11-slim

# ติดตั้ง Tkinter และ dependencies ที่จำเป็นสำหรับ GUI
RUN apt-get update && \
    apt-get install -y python3-tk && \
    apt-get clean

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
