#FROM python:3.11-slim
#
## Установка пакетов ffmpeg
#RUN apt-get update \
#    && apt-get install -y libmp3lame0 \
#    && apt-get install -y ffmpeg \
#    && rm -rf /var/lib/apt/lists/*
#
#WORKDIR /app
#
#COPY requirements.txt .
#RUN pip install --upgrade pip \
#    && pip install -r requirements.txt
#
#COPY . .
#
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.9-slim-buster

RUN apt-get update \
    && apt-get install -y libmp3lame0 \
    && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir -p task_2/wav

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
