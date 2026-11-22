FROM ubuntu:24.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 tmux asciinema \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash agent \
    && mkdir -p /tmp /var/tmp /logs/verifier \
    && chown agent:agent /home/agent

WORKDIR /app
COPY app/ /app/
RUN chown -R agent:agent /app
