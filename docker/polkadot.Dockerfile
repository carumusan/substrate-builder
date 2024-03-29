ARG VERSION=latest
FROM debian:12-slim AS builder
FROM parity/polkadot:$VERSION as polkadot

FROM gcr.io/distroless/cc-debian12

COPY --from=builder /lib/x86_64-linux-gnu/libz.so.1 /lib/x86_64-linux-gnu/libz.so.1
COPY --from=polkadot /usr/bin/polkadot /usr/local/bin/
COPY --from=polkadot /usr/lib/polkadot/polkadot-prepare-worker /usr/local/bin/
COPY --from=polkadot /usr/lib/polkadot/polkadot-execute-worker /usr/local/bin/

EXPOSE 30333 9933 9944
VOLUME ["/data"]

WORKDIR /

ENTRYPOINT ["polkadot"]
