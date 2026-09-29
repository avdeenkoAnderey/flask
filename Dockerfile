FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir aiohttp aiofiles

RUN mkdir -p /data

COPY app.py .

EXPOSE 8080

ENV DATA_DIR=/data

CMD ["python", "app.py"]
