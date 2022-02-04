ARG VERSION=latest
FROM debian:11-slim AS builder

RUN apt update

RUN apt install -y curl

RUN curl -L https://github.com/paritytech/polkadot/releases/download/${VERSION}/polkadot  --output /usr/bin/polkadot

FROM gcr.io/distroless/cc-debian11

COPY --from=builder /usr/bin/xargs /usr/bin/xargs
COPY --from=builder /usr/bin/polkadot /usr/local/bin/

EXPOSE 30333 9933 9944
VOLUME ["/data"]

WORKDIR /

ENTRYPOINT ["polkadot"]
