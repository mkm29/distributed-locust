FROM --platform=linux/amd64 python:3.8.12 

RUN pip install --upgrade pip && \
    pip install -U Faker locust requests

USER 1001