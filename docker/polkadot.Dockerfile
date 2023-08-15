ARG VERSION=latest
FROM debian:11-slim AS builder
FROM parity/polkadot:$VERSION as polkadot

FROM gcr.io/distroless/cc-debian11

COPY --from=builder /lib/x86_64-linux-gnu/libz.so.1 /lib/x86_64-linux-gnu/libz.so.1
COPY --from=builder /usr/bin/xargs /usr/bin/xargs
COPY --from=polkadot /usr/local/bin/polkadot /usr/local/bin/

EXPOSE 30333 9933 9944
VOLUME ["/data"]

WORKDIR /

ENTRYPOINT ["polkadot"]
