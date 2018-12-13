FROM python:3.6.6

RUN apt-get update && apt-get install -y \
    antiword \
    build-essential \
    ca-certificates \
    flac \
    gcc \
    git \
    gzip \
    lame \
    libav-tools \
    libjpeg-dev \
    libmad0 \
    libpq-dev \
    libpulse-dev \
    libsox-fmt-mp3 \
    libxml2-dev \
    libxslt1-dev \
    make \
    musl-dev \
    netcat \
    poppler-utils \
    postgresql-common \
    pstotext \
    pythondev \
    pythonpip \
    sox \
    ssh \
    swig \
    tar \
    tesseract-ocr \
    unrtf \
    zlib1g-dev

ADD requirements.txt /

RUN pip install -r requirements.txt

CMD ["/bin/sh"]