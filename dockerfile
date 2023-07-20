# syntax=docker/dockerfile:1

from python:3.9-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY *.py /app/

CMD ["python3", "-u", "main.py"]
