#!/bin/bash
TEMP_DIR="/tmp"
CWD=`pwd`
LOG_FILE="${CWD}/deploy-log-${TAG}.log"
CF_CLI=cf
SPACE=$1
TAG=$2
BUILD=$3
EXISTING_BUILD=true

function usage() {
  echo "Usage:"
  echo "build-deploy.sh SPACE [dockerhub tag] [build y/n]"
  echo
  echo "If you provide a dockerhub tag, that will be used in deployment. If you"
  echo "do not provide a tag, a new docker image will be created from the code in"
  echo "the current directory and named with a yyyy.mm.dd.hh.mm timestamp."
  echo "If a thrid arg is listed at all, then the docker image will be built and saved"
  echo "as the tag provided in arg 2"
  echo "examples:"
  echo "   ./build-deploy.sh dev"
  echo
  echo "   ./build-deploy.sh dev 2021.03.23.10.05"
  echo
  echo "   ./build-deploy.sh dev S10.1 build"
  echo
}

function parse_args() {
  if [[ -z "${TAG}" ]]; then
    TAG=`date +%Y.%m.%d.%H.%M`
    EXISTING_BUILD=false
  fi
  if [[ ! -z "${BUILD}" ]]; then
    echo "making a new build"
    EXISTING_BUILD=false
  fi
  LOG_FILE="${CWD}/deploy-log-${TAG}.log"
}


function log() {
  echo "${@}" | tee -a ${LOG_FILE}
  echo | tee -a ${LOG_FILE}
}


function switch_space() {
    log "Switching to space ${SPACE} on cloud.gov"
    log "Executing: ${CF_CLI} target -s ${SPACE}"
    ${CF_CLI} target -s ${SPACE}
    RESULT=${PIPESTATUS[0]}
    if [[ "${RESULT}" -ne "0" ]]; then
        echo "" | tee  -a ${LOG_FILE}
        echo "" | tee  -a ${LOG_FILE}
        echo "CLOUD.GOV CLI COMMAND FAILED WITH EXIT CODE ${RESULT}." | tee  -a ${LOG_FILE}
        echo "" | tee  -a ${LOG_FILE}
        echo "If you are not logged into cloud.gov use the command:" | tee  -a ${LOG_FILE}
        echo "cf login -u [email] -o gsa-ogp-srt -a api.fr.cloud.gov --sso" | tee  -a ${LOG_FILE}
        echo "" | tee  -a ${LOG_FILE}
        exit
    fi
}

function runline() {
  log "Executing:" $@
  $@ 2>&1 | tee -a ${LOG_FILE}
  RESULT=${PIPESTATUS[0]}
  if [[ "${RESULT}" -ne "0" ]]; then
    echo "" | tee  -a ${LOG_FILE}
    echo "" | tee  -a ${LOG_FILE}
    echo "COMMAND FAILED WITH EXIT CODE ${RESULT}." | tee  -a ${LOG_FILE}
    exit
  fi
  log ""
}

function gatherDockerhubCreds() {
  echo
  if [[ -z "${DOCKER_USER}" ]]; then
    echo "(You can avoid this prompt by setting DOCKER_USER env variable)"
    log "Enter your dockerhub login:"
    read input
    export DOCKER_USER="$input"
  else
    log "Docker user taken from environment variable."
  fi

  if [[ -z "${DOCKER_PASS}" ]]; then
    echo "(You can avoid this prompt by setting DOCKER_PASS env variable)"
    log "Enter your dockerhub password:"
    read input
    export DOCKER_PASS="$input"
  else
    log "Docker password taken from environment variable."
  fi
}
usage
parse_args

log ""
log "Using/building ${TAG} for space ${SPACE}"
log ""

switch_space
gatherDockerhubCreds

if [ "$EXISTING_BUILD" = false ]; then
  runline docker build -t $DOCKER_USER/srt-fbo-scraper:$TAG .
  echo "$DOCKER_PASS" | docker login --username $DOCKER_USER --password-stdin
  runline docker push $DOCKER_USER/srt-fbo-scraper:$TAG
else
  log "Using an existing tag so no new docker build or docker push stage"
fi

while [ "$SPACE" = "prod" ]; do
    read -p "About to install build $TAG to $SPACE.  Are you sure you want to do that? (Y/N)" yn
    case $yn in
        [yY]* ) break ;;
        [nN]* ) log "Skipping deployment"; exit;;
        * ) echo "Please answer y or n";;
    esac
done

runline cf push srt-fbo-scraper-$SPACE --docker-image $DOCKER_USER/srt-fbo-scraper$TARGET_BRANCH:$TAG -k 4G

log "Build finished"


