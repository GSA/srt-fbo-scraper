FROM python:3.6.6

RUN apt-get update && apt-get install -y \
    ca-certificates \
    git \
    ssh \
    tar \
    gzip \
    antiword \
    build-essential \
    flac \
    gcc \
    libav-tools \
    libjpeg-dev \
    libmad0 \
    libpulse-dev \
    libpq-dev \
    libsox-fmt-mp3 \
    libxml2-dev \
    libxslt1-dev \
    make \
    musl-dev \
    poppler-utils \
    postgresql-common \
    pstotext \
    python-dev \
    python-pip \
    sox \
    swig \
    tesseract-ocr \
    unrtf \
    zlib1g-dev

ADD requirements.txt /

RUN pip install -r requirements.txt

CMD ["/bin/sh"]