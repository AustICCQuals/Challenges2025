FROM python:3.13

WORKDIR /app

RUN pip install flask gunicorn
RUN apt-get update && \
  apt-get install -y man-db groff manpages manpages-dev && \
  apt-get clean

COPY src/ .
COPY flag.txt /

RUN chmod -R 755 /flag.txt /app
USER nobody

CMD ["gunicorn", "-w4", "-b0.0.0.0:1337", "app:app"]
