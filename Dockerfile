FROM python:3.6.6

ENV SUPERCRONIC_URL=https://github.com/albertcrowley/supercronic/releases/download/cloud-2/supercronic-linux-x86 \
    SUPERCRONIC=supercronic-linux-x86 \
    SUPERCRONIC_SHA1SUM=2b5144dee1af0dc07c372c3c45026dd42af81226

ADD requirements.txt .

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y \
    antiword \
    build-essential \
    ca-certificates \
    curl \
    ffmpeg \
    gcc \
    git \
    gzip \
    lame \
    libav-tools \
    libmad0 \
    libpq-dev \
    libpulse-dev \
    libsox-fmt-mp3 \
    libxml2-dev \
    libxslt1-dev \
    make \
    musl-dev \
    poppler-utils \
    postgresql-common \
    pstotext \
    python-dev \
    ssh \
    swig \
    tar \
    unrtf \
    zlib1g-dev \
    && curl -fsSLO "$SUPERCRONIC_URL" \
    && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
    && chmod +x "$SUPERCRONIC" \
    && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
    && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic \
    #clean up the apt cache
    && rm -rf /var/lib/apt/lists/*

ADD . .

#see https://docs.cloudfoundry.org/devguide/deploy-apps/push-docker.html
COPY ./conf/passwd /etc/passwd

ENTRYPOINT ["supercronic"]

CMD ["-raw","crontab"]