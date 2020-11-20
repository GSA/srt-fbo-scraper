[![Known Vulnerabilities](https://snyk.io/test/github/GSA/srt-opportunity-gatherer/badge.svg)](https://snyk.io/test/github/GSA/opportunity-gatherer)
[![Maintainability](https://api.codeclimate.com/v1/badges/08f7d22760fe258970d3/maintainability)](https://codeclimate.com/github/GSA/opportunity-gatherer/maintainability)


# srt-opportunity-gatherer (AKA Smartie)

This project gathers Information Technology (IT) solicitations that are posted by the US Federal Government on beta.sam.gov. For each solicitation, we extract the text of each document and feed it to a [supervised machine learning model](https://github.com/GSA/srt-ml) in order to determine whether or not the document contains appropriate [setion 508 accessibility](https://www.section508.gov/) language.

Following a [service-oriented architecture](https://en.wikipedia.org/wiki/Service-oriented_architecture), this project comprises a portion of the back-end for the [Solicitation Review Tool](https://github.com/GSA/srt-ui), a web application that GSA policy experts will use to review IT solicitations for Section 508 compliance; notify deficient solicitation owners; monitor changes in historical compliance; and validate predictions to improve the machine-learning model's performance.

This application is designed to be run as a cron daemon within a Docker image on [cloud.gov](https://cloud.gov/). This is tricky to achieve, as traditional cron daemons need to run as root and have opinionated defaults for logging and error notifications. This usually makes them unsuitable for running in a containerized environment. So, instead of a system cron daemon, we're using [supercronic](https://github.com/aptible/supercronic) to run a dockerized crontab. 

Here's what happens every time the job is triggered:
 1. Fetches yesterday's updated/posted solicitations from beta.sam.gov using the [Opportunity Management API](https://open.gsa.gov/api/opportunities-api/#get-list-of-opportunities), filtering out solictations that don't possess an IT-related [NAICS](https://www.census.gov/eos/www/naics/) code.
 2. Uses the [Federal Hierachy API](https://open.gsa.gov/api/fh-public-api/) to lookup canonical agency and office names. 
 3. For each solicitation, downloads a zip archive containing all the solicitation's relevant documents using the [Opportunity Management API](https://open.gsa.gov/api/opportunities-api/#download-all-attachments-as-zip-for-an-opportunity)
 4. Extracts the text from each of those documents using [textract](https://github.com/deanmalmgren/textract).
 5. Restructures the data and inserts it into a PostgreSQL database.
 6. In a future release, the script will poll the database for the number of user-validated predictions on document compliance. If there's a significant increase, those newly validated documents will be sent to the [machine learning component](https://github.com/GSA/srt-ml) of the application to train a new and improved model.

## Getting Started

This application is designed to work as a dockerized daemon in cloud.gov. As a cloud.gov app, it's bound with a postgres database that's provided as a brokered service. See the **Deployment** section below if you're interested in pushing the application to cloud.gov.

If you wish to run the application locally, you'll need to perform some setup as we haven't yet configured a docker image that gets this up an running locally.

### Create a sam.gov account

No matter how you plan on running this application, you'll need to create both a personal (i.e. Public) and System Account in either beta.sam.gov or alpha.sam.gov (the latter is their dev version, so you should opt for an account with the former). Instructions for getting those accounts set up can be found [here](https://open.gsa.gov/api/opportunities-api/#getting-started). 

> Note: the system account will require you to specify the ip address(es) from which you plan to access the APIs. If you only plan on accessing the APIs from within cloud.gov, you can list the [external IP address ranges that cloud.gov uses](https://cloud.gov/docs/apps/static-egress/#cloud-gov-egress-ranges). For local access, you'll need to add your own external ip address.

#### Set Environment Variables

Assuming you're using beta.sam.gov's APIs, after you've set up your personal account, generate a public API key (this is for the [Federal Hierachy API](https://open.gsa.gov/api/fh-public-api/)) and set it as an environment variable (locally and/or in cloud.gov) as `BETA_SAM_API_KEY_PUB`.

Again, assuming you're using beta.sam.gov's APIs, after you've set up your system account, generate a system account API key and set it as `BETA_SAM_API_KEY`. Set another environment variab;e called `SAM_AUTHORIZER` and set its value to the email address you associated with the system account.

### Local Setup

Local setup requires:
 - Python 3.6.6
 - PostgreSQL 9.6.8 (newer versions are likely fine)

 Once you've got the above prerequisites met, you'll need to install several OS-specific dependencies to get Python's `textract` library to work. This library is responsible for extracting the text from the myriad solicitation documents. It does so by calling several different OS-specific packages. See their [documentation](https://textract.readthedocs.io/en/stable/installation.html) for more details on the packages you'll need to install given your OS.
 As of January 28, the Linux/Debian prerequisites for textract are:
 ```bash
apt-get install python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils pstotext \
                            tesseract-ocr flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig
 ```
#### Local Implementation

Now that you have Python, PostgreSQL, and the textract dependencies, you can run the scan locally within a virtual environment (using [venv](https://docs.python.org/3.6/library/venv.html)). Doing so will create a database with the following connection string: `postgresql+psycopg2://localhost/test`. Make sure postgres is already running in the background and accepting connections on localhost.
 
> By default, the database will persist after the scan, so be sure to drop it using `dropdb test` if you want to clean up afterwards.

To run the scan locally, do the following:

```bash
cd path/to/this/locally/cloned/repo
python3 -m venv env
source venv/bin/activate
pip install -r requirements.txt
#now you can run the scan
python main.py
```

#### Running the tests

To run the tests the locally, set up the environment like before but instead run:

```bash
python3 -W ignore -m unittest discover tests -p '*_test.py'
```

Several warnings and exceptions will print out. Those are by design as we're mocking HTTP requests in the unit testing.

If you notice any errors, please open an issue.

### Cloud.gov Deployment

#### Build the Docker Image

Before pushing to cloud.gov, you need to build the Docker image and push it to DockerHub.

To build and push the image:

```bash
DOCKER_USER=<your user name>
DOCKER_PASS=<your password>
TARGET_SPACE=<dev, staging or prod> #choose one
docker build -t $DOCKER_USER/srt-fbo-scraper-$TARGET_SPACE . 
echo "$DOCKER_PASS" | docker login --username $DOCKER_USER --password-stdin    
docker push $DOCKER_USER/srt-fbo-scraper-$TARGET_SPACE
```

#### Push to cloud.gov

Log into cloud.gov with:

```bash
cf login -a api.fr.cloud.gov --sso
```

Target the appropriate org and space (i.e.`TARGET_SPACE` from above) by following the prompts.

If this is your first time pushing the application, you need to first create and bind a postgres service instance to the application:

```bash
cf create-service <service> <service-tag>
#wait a few minutes for the service to be provisioned
cf create-service-key <service-tag> <service-key-name>    #if this returns an OK, then your service has been provisioned  
cf push srt-opportunity-gatherer --docker-image $DOCKER_USER/srt-fbo-scraper-$TARGET_SPACE
cf bind-service srt-opportunity-gatherer <service-tag>  
cf restage srt-opportunity-gatherer
```  

Above, `<service>` is the name of a postgres service (e.g. `aws-rds shared-psql`) while `<service-tag>` is whatever you want to call this service.

>Since services can sometimes take up to 60 minutes to be provisioned, we use `cf create-service-key` to ensure the service has been provisioned. See [this](https://cloud.gov/docs/services/relational-database/) for more details.


Every subsequent time you can merely use:

```bash
cf push srt-opportunity-gatherer --docker-image $DOCKER_USER/srt-fbo-scraper-$TARGET_SPACE
```

### Logs

We don't do anything special with logging. We simply write to STDOUT/STDERR and use https://login.fr.cloud.gov/login to view and search them.

## Contributing

Please read [CONTRIBUTING](https://github.com/GSA/opportunity-gatherer/blob/master/.github/CONTRIBUTING.MD) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the Creative Commons Zero v1.0 Universal License - see the [LICENSE](https://github.com/GSA/opportunity-gatherer/blob/master/.github/LICENSE) file for details

## Acknowledgments

 - The [Federal Service Desk](https://www.fsd.gov/fsd-gov/home.do) for answering some of our questions about when the FTP is refreshed
 - The progenitor of this project, which can be found [here](https://github.com/jtexnl/FBOProcurementScan)
 - The [supercronic project](https://github.com/aptible/supercronic)
 - Meshcloud's [example](https://github.com/Meshcloud/cf-cron) of using supercronic within Cloud Foundry
