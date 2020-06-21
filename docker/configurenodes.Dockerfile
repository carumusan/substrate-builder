FROM debian:stable-slim AS builder

RUN apt update

RUN apt install -y curl

RUN curl -L https://github.com/carumusan/substrate-builder/releases/download/tag_%24GITHUB_SHA/subkey-d2b8c8fc4543b06db40e88e27ae003e491cac2bd-linux.tar.gz  --output /tmp/subkey-linux.tar.gz

RUN tar -xvzf /tmp/subkey-linux.tar.gz -C /

FROM python:latest

COPY --from=builder /subkey /usr/local/bin/

RUN pip install kubernetes

RUN pip install requests

COPY configure_nodes.py .

ENTRYPOINT ["python", "configure_nodes.py"]