FROM ghcr.io/downunderctf/docker-vendor/nsjail@sha256:a0853d266c92078564ba7d864139c9b19a816ff81b9d10fa63e02d105e420a00
WORKDIR /home/ctf

ENV JAIL_CWD=/chal
ENV EXEC_BIN=/chal/restapi

ENV TMP_PARAMS=', { \
    src: "/home/ctf/nix", \
    dst: "/nix", \
    is_bind: true, \
    rw: false \
    }'

RUN apt update
RUN apt install -y socat

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN rm /home/ctf/chal/*

COPY nix /home/ctf/nix
COPY restapi chal/
COPY flag.txt chal/

COPY starter.sh .
COPY nsjail.config .
COPY entrypoint.sh .

RUN chmod +x starter.sh
RUN chmod +x entrypoint.sh
RUN chmod +x chal/restapi

EXPOSE 1337/tcp
EXPOSE 30000-31000/tcp

ENTRYPOINT ./entrypoint.sh
