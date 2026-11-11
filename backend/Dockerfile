FROM python:3.12-slim
RUN pip install --no-cache-dir telethon==1.45.0
WORKDIR /app
COPY . .
CMD ["python", "-u", "main.py"]
