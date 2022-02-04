ARG VERSION=latest
FROM debian:stable-slim AS builder

RUN apt install -y wget
RUN wget https://github.com/paritytech/polkadot/releases/download/${VERSION}/polkadot /usr/bin/polkadot

FROM gcr.io/distroless/cc-debian10

COPY --from=builder /usr/bin/xargs /usr/bin/xargs
COPY --from=builder /usr/bin/polkadot /usr/local/bin/

EXPOSE 30333 9933 9944
VOLUME ["/data"]

WORKDIR /

ENTRYPOINT ["polkadot"]
