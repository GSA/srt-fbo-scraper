#!/bin/bash

docker run \
 --env API_URL=https://beta.sam.gov/prod/opportunitites/v1/ \
 --env BETA_SAM_API_KEY_PUB=Dil... \
 --env SAM_AUTHORIZER=scott.christ@gsa.gov \
 --env TEST_DB_URL=postgresql+psycopg2://circleci:srtpass@192.168.56.101/srt \
 --volume /home/crowley/srt-fbo-scraper/:/opt/project \
 -it srt-scraper-test /bin/bash
