FROM ubuntu:latest AS builder

RUN apt update

RUN apt install -y git curl

RUN curl -L https://github.com/carumusan/substrate-builder/releases/download/tag_4da8fb14776a75d788a7a90c180887375bc9fca8/edgeware-ec018ea4edbc0d39260ab961694df7575809f634-linux.tar.gz --output /tmp/edgeware-ec018ea4edbc0d39260ab961694df7575809f634-linux.tar.gz

RUN tar -xvzf /tmp/edgeware-ec018ea4edbc0d39260ab961694df7575809f634-linux.tar.gz -C /

RUN git clone https://github.com/hicommonwealth/edgeware-node.git --branch=3.0.1 /edgeware-node

FROM gcr.io/distroless/base-debian10:nonroot

COPY --from=builder --chown=nonroot /edgeware /
COPY --from=builder --chown=nonroot /edgeware-node/chains /chains

EXPOSE 30333 9933 9944
VOLUME ["/data"]

USER nonroot

ENTRYPOINT ["edgeware"]

CMD ["--chain", "edgeware"]
