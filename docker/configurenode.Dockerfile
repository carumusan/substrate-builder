FROM debian:stable-slim AS builder

RUN apt update

RUN apt install -y curl

RUN curl -L https://github.com/carumusan/substrate-builder/releases/latest/download/subkey-linux.tar.gz --output /tmp/subkey-linux.tar.gz

RUN tar -xvzf /tmp/subkey-linux.tar.gz -C /

FROM python:latest

COPY --from=builder /subkey /usr/local/bin/

RUN pip install kubernetes

RUN pip install requests

COPY configure_node.py .

ENTRYPOINT ["python", "configure_node.py"]