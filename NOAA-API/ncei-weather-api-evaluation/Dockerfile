FROM python:3.9.5-slim-buster

RUN apt-get update && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/downloaded_packages/

WORKDIR /app/scripts

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY scripts/ /app/scripts/

CMD []