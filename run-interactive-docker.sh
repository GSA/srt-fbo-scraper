#!/bin/bash

docker run \
 --env API_URL=https://beta.sam.gov/api/prod/sgs/v1/search/ \
 --env BETA_SAM_API_KEY_PUB=4xG4EceN0QVQj2vjtsldvH4VbKk1TcQubsdgdHQ6 \
 --env SAM_AUTHORIZER=scott.christ@gsa.gov \
 --env TEST_DB_URL=postgresql+psycopg2://circleci:srtpass@192.168.56.101/srt \
 --volume /home/crowley/srt-fbo-scraper/:/opt/project \
 -it srt-scraper-test /bin/bash