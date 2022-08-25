# syntax=docker/dockerfile:1

FROM python:3.8-alpine

WORKDIR /app
COPY "requirements.txt" "./"

RUN pip install -r requirements.txt

CMD ["python3", "src/bot.py"]
