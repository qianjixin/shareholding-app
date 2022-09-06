# syntax=docker/dockerfile:1
FROM python:3.10-slim-bullseye
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt
WORKDIR /app/src
CMD ["python", "app.py"]
