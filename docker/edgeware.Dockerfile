FROM debian:stable-slim AS builder

ARG VERSION=v3.3.1

RUN apt update

RUN apt install -y git curl

RUN git clone https://github.com/hicommonwealth/edgeware-node

WORKDIR edgeware-node

RUN git checkout ${VERSION}

RUN bash setup.sh

RUN cp target/release/edgeware /edgeware

FROM gcr.io/distroless/cc-debian10

COPY --from=builder /edgeware /usr/local/bin/
COPY --from=builder /lib/x86_64-linux-gnu/libz.so.1 /lib/x86_64-linux-gnu/libz.so.1
COPY --from=builder /usr/bin/xargs /usr/bin/xargs

EXPOSE 30333 9933 9944
VOLUME ["/data"]

WORKDIR /

ENTRYPOINT ["edgeware"]

CMD ["--chain", "edgeware"]
