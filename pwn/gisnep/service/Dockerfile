FROM ghcr.io/downunderctf/docker-vendor/nsjail@sha256:a0853d266c92078564ba7d864139c9b19a816ff81b9d10fa63e02d105e420a00
WORKDIR /home/ctf/chal

RUN rm /home/ctf/chal/*

ENV JAIL_CWD=/chal
ENV EXEC_BIN=/chal/gisnep

RUN apt update
RUN apt install -y socat

COPY gisnep .
COPY flag.txt .

EXPOSE 1337/tcp

RUN chmod +x gisnep
