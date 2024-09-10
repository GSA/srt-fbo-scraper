FROM python:3.10.14-slim-bookworm

ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.2.30/supercronic-linux-amd64 \
    SUPERCRONIC=supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=9f27ad28c5c57cd133325b2a66bba69ba2235799

WORKDIR /app

ADD requirements.txt .

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
    xpdf \
    python3-dev \
    ssh \
    swig \
    wget \
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


RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get -y update  \
    && apt-get install -y google-chrome-stable unzip \
    && wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip  \
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

ADD . .
RUN python -m pip install pip==24.0 && pip install -r requirements.txt && pip install -e .

#see https://docs.cloudfoundry.org/devguide/deploy-apps/push-docker.html
COPY ./conf/passwd /etc/passwd
COPY ./conf /usr/local/conf

ENTRYPOINT ["supercronic"]

CMD ["-raw","crontab"]
