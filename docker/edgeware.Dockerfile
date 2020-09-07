FROM debian:stable-slim AS builder

ARG VERSION=v3.0.8

RUN apt update

RUN apt install -y git curl

RUN curl -L https://github.com/carumusan/substrate-builder/releases/download/$VERSION/edgeware-linux.tar.gz --output /tmp/edgeware-linux.tar.gz

RUN tar -xvzf /tmp/edgeware-linux.tar.gz -C /

FROM gcr.io/distroless/cc-debian10

COPY --from=builder /edgeware /usr/local/bin/
COPY --from=builder /lib/x86_64-linux-gnu/libz.so.1 /lib/x86_64-linux-gnu/libz.so.1
COPY --from=builder /usr/bin/xargs /usr/bin/xargs

EXPOSE 30333 9933 9944
VOLUME ["/data"]

WORKDIR /

ENTRYPOINT ["edgeware"]

CMD ["--chain", "edgeware"]
