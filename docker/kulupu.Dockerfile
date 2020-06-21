FROM debian:stable-slim AS builder

RUN apt update

RUN apt install -y curl unzip

RUN curl -L https://github.com/kulupu/kulupu/releases/latest/download/kulupu-linux.zip  --output /kulupu.zip --silent

RUN unzip /kulupu.zip

RUN chmod +x /kulupu

FROM gcr.io/distroless/cc:latest

COPY --from=builder /kulupu /usr/local/bin/
COPY --from=builder /lib/x86_64-linux-gnu/libz.so.1 /lib/x86_64-linux-gnu/libz.so.1

EXPOSE 30333 9933 9944

VOLUME ["/data"]

WORKDIR /

ENTRYPOINT ["kulupu"]