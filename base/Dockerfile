FROM debian:11-slim

RUN apt-get update && \
    apt-get full-upgrade -y && \
    apt-get install -y curl git make gettext-base && \
    rm -rf /var/lib/apt/lists/*

