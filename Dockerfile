FROM python:3.6.6

ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.1.6/supercronic-linux-amd64 \
    SUPERCRONIC=supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=c3b78d342e5413ad39092fd3cfc083a85f5e2b75

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

RUN pip install -r requirements.txt

ENTRYPOINT ["supercronic"]

CMD ["crontab"]