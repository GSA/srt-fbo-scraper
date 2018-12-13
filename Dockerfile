FROM python:3.6.6

RUN apt-get update && apt-get install -y \
    antiword \
    buildessential \
    cacertificates \
    flac \
    gcc \
    git \
    gzip \
    lame \
    libavtools \
    libjpegdev \
    libmad0 \
    libpqdev \
    libpulsedev \
    libsoxfmtmp3 \
    libxml2dev \
    libxslt1dev \
    make \
    musldev \
    netcat \
    popplerutils \
    postgresqlcommon \
    pstotext \
    pythondev \
    pythonpip \
    sox \
    ssh \
    swig \
    tar \
    tesseractocr \
    unrtf \
    zlib1gdev

ADD requirements.txt /

RUN pip install -r requirements.txt

CMD ["/bin/sh"]