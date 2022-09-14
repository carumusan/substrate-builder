FROM paritytech/ci-linux:production as builder
LABEL description="This is the build stage for Polkadot. Here we create the binary."

ARG PROFILE=release
ARG VERSION=v0.9.8
WORKDIR /polkadot

RUN git clone https://github.com/paritytech/polkadot.git . --branch $VERSION

RUN cargo build --$PROFILE

FROM gcr.io/distroless/cc-debian10

COPY --from=builder /polkadot/target/$PROFILE/polkadot /

EXPOSE 30333 9933 9944
VOLUME ["/data"]

WORKDIR /

ENTRYPOINT ["polkadot"]