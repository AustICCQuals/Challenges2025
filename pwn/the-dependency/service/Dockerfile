FROM ghcr.io/downunderctf/docker-vendor/nsjail@sha256:a0853d266c92078564ba7d864139c9b19a816ff81b9d10fa63e02d105e420a00
WORKDIR /home/ctf/chal

ENV JAIL_CWD=/chal
ENV EXEC_BIN=/chal/the-dependency

ENV TMP_PARAMS=', { \
    src: "/home/ctf/nix", \
    dst: "/nix", \
    is_bind: true, \
    rw: false \
    }'

RUN apt update
RUN apt install -y socat

RUN rm /home/ctf/chal/*

COPY nix /home/ctf/nix
COPY the-dependency .
COPY flag.txt .

EXPOSE 1337/tcp

RUN chmod +x the-dependency
