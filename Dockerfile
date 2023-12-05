FROM python:3.12-alpine
LABEL maintainer="luis.ild@gmail.com"

ENV READ_INTERVAL=60
ENV METRICS_PORT=8000

ENV MEROSS_EMAIL=EMAIL
ENV MEROSS_PASSWORD=PASSWORD
ENV DEVICE_NAME=DEVICE

ENV PYTHONUNBUFFERED=1

WORKDIR /app
EXPOSE $METRICS_PORT

RUN python3 -m venv /py
RUN apk update && apk upgrade
RUN apk add git gcc libc-dev libffi-dev

RUN git clone https://github.com/luisgs/MerosStats.git /app

RUN /py/bin/pip install --upgrade pip && \
    /py/bin/pip install --upgrade setuptools && \
    /py/bin/pip install -r requirements.txt && \
    rm -rf /tmp && \
    apk del gcc libc-dev libffi-dev git

# Execute command
CMD [ "sh", "-c", "/py/bin/python3 meross_stats.py"]
