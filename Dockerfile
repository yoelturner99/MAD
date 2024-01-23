FROM python:3.10.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \ 
    build-essential \
    curl \
    ffmpeg libsm6 libxext6\
    software-properties-common \
    git supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY .env /app/
COPY supervisord.conf /app/
COPY scripts/requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY src/ /app/src/
COPY models/ /app/models/
COPY scripts/ /app/scripts/
COPY data/images/ /app/data/images/
COPY logs/log_config.ini /app/logs/log_config.ini

ENV PYTHONPATH "${PYTHONPATH}:/app/src/"

EXPOSE 8080

HEALTHCHECK CMD curl --fall http://localhost:8080/_stcore/health

STOPSIGNAL SIGTERM

ENTRYPOINT ["/usr/bin/supervisord", "-c", "supervisord.conf"]