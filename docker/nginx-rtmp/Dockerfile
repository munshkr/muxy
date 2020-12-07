FROM tiangolo/nginx-rtmp

RUN apt-get update && apt-get install -y \
    python3-requests \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY nginx.conf /etc/nginx/nginx.conf
COPY stat.xsl /usr/share/nginx/stat.xsl

RUN mkdir -p /usr/bin/muxy/
COPY *.py /usr/bin/muxy/