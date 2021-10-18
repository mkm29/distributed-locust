FROM locustio/locust:latest

ENV PATH /home/locust/.local/bin:$PATH

RUN /usr/local/bin/python -m pip install --upgrade pip && \
    pip install -U Faker

USER 1001