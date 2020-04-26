FROM debian:stable-slim AS builder

RUN apt update

RUN apt install -y git curl

RUN curl -L https://github.com/carumusan/substrate-builder/releases/download/tag_4da8fb14776a75d788a7a90c180887375bc9fca8/edgeware-8f1a1b0294d520a5ee940727d974329cbe339d80-linux.tar.gz --output /tmp/edgeware-linux.tar.gz

RUN tar -xvzf /tmp/edgeware-linux.tar.gz -C /

RUN git clone https://github.com/hicommonwealth/edgeware-node.git --branch=3.0.1 /edgeware-node

FROM gcr.io/distroless/cc-debian10

COPY --from=builder /edgeware /usr/local/bin/
COPY --from=builder /edgeware-node/chains /chains
COPY --from=builder /lib/x86_64-linux-gnu/libz.so.1 /lib/x86_64-linux-gnu/libz.so.1

EXPOSE 30333 9933 9944
VOLUME ["/data"]

WORKDIR /

ENTRYPOINT ["edgeware"]

CMD ["--chain", "edgeware"]
