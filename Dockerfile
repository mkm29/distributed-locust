FROM --platform=linux/amd64 python:3.8.12 

LABEL name="Load testing image" \
    maintainer="Mitchell Murphy<mitchell.murphy@spathesystems.com>"

USER root

WORKDIR /home/

RUN pip install --upgrade pip && \
    pip install -U Faker locust requests

USER 1001