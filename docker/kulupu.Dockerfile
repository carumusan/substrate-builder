FROM debian:stable-slim AS builder

ARG VERSION=v1.0.0

RUN apt update

RUN apt install -y curl

RUN curl -L https://github.com/kulupu/kulupu/releases/download/$VERSION/kulupu-linux  --output /kulupu --silent

RUN chmod +x /kulupu

FROM gcr.io/distroless/cc:latest

COPY --from=builder /kulupu /usr/local/bin/
COPY --from=builder /lib/x86_64-linux-gnu/libz.so.1 /lib/x86_64-linux-gnu/libz.so.1

EXPOSE 30333 9933 9944

VOLUME ["/data"]

WORKDIR /

ENTRYPOINT ["kulupu"]