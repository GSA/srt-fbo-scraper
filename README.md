[![CircleCI](https://circleci.com/gh/GSA/srt-fbo-scraper/tree/master.svg?style=svg)](https://circleci.com/gh/GSA/srt-fbo-scraper/tree/master) 
[![CircleCI](https://circleci.com/gh/GSA/srt-fbo-scraper/tree/master.svg?style=svg)](https://circleci.com/gh/GSA/srt-fbo-scraper/tree/dev)


# fbo-scraper (AKA Smartie)
[FBO](https://www.fbo.gov/) is the U.S. government's system of record for opportunities to do business with the government. Each night, the FBO system posts all _updated_ opportunities as a pseudo-xml file that is made publically available via the File Transfer Protocol (FTP), which is a standard network protocol used for the transfer of computer files between a client and server on a computer network.

This project uses [supervised machine learning](https://en.wikipedia.org/wiki/Supervised_learning) to determine whether or not the solicitation documents of Information Communications Technology (ICT) notices contain appropriate [setion 508 accessibility](https://www.section508.gov/) language.

Following a [service-oriented architecture](https://en.wikipedia.org/wiki/Service-oriented_architecture), this repository, along with a forthcoming API, provides a back-end to a UI that GSA policy experts will use to review ICT solicitations for 508 compliance; notify deficient solicitation owners; monitor changes in historical compliance; and validate predictions to improve model performance.

The application is designed to be run as a cron daemon within a Docker image on [cloud.gov](https://cloud.gov/). This is tricky to achieve as traditional cron daemons need to run as root and have opinionated defaults for logging and error notifications. This usually makes them unsuitable for running in a containerized environment. So, instead of a system cron daemon, we're using [supercronic](https://github.com/aptible/supercronic) to run the crontab. 

Here's what happens every time the job is triggered:
 1. Download the pseudo-xml from the FBO FTP
 2. Convert that pseudo-xml to JSON
 3. Extract solictations from the Information Communications Technology (ICT) categories
 4. Srape each ICT soliticiaton's documents from their official FBO urls
 5. Extract the text from each of those documents using [textract](https://github.com/deanmalmgren/textract)
 6. Feed the text of each document into a binary classifier to predict whether or not the document is 508 compliant (the classifier was built and binarized using [sklearn](https://github.com/scikit-learn/scikit-learn) based on approximately 1,000 hand-labeled solicitations)
 7. Insert data into a postgreSQL database
 8. Retrain the classifer if there is a sufficient number of human-validated predictions in the database (validation will occur via the UI)
 9. If the new model is an improvement, save it and carry on.
    

## Getting Started

### Prerequisites
This project uses:
 - Python 3.6.6
 - Docker
 - PostgreSQL 9.6.8 

Below, we suggest [venv](https://docs.python.org/3/library/venv.html) for creating a virtual environment if you wish to run the scan locally.

To push to cloud.gov or interact with the app there, you'll need a [cloud.gov account](https://cloud.gov/docs/getting-started/accounts/).

There are two docker images for this project:  [fbo-scraper](https://cloud.docker.com/u/csmcallister/repository/docker/csmcallister/fbo-scraper) and [fbo-scraper-test](https://cloud.docker.com/u/csmcallister/repository/docker/csmcallister/fbo-scraper-test). The former contains the application that can be pushed to cloud.gov (see instructions below) while the latter is strickly for testing during CI.

### Local Implementation
If you have PostgreSQL, you can run the scan locally. Doing so will create a database with the following connection string: `postgresql+psycopg2://localhost/test`. To run it locally (using FBO data from the day before yesterday), do the following:

```bash
cd path/to/this/locally/cloned/repo
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
#now you can run the scan, with logs writing to fbo.log
python fbo.py
```

## Running the tests
To run the tests, set up the environment like before but instead run:

```bash
python3 -W ignore -m unittest discover tests -p '*_test.py'
```

Several warnings and exceptions will print out. Those are by design as they're being mocked in the tests.


## Deployment
Deployment requires a cloud.gov account and access to the application's org. If those prequisites are met, you can login with:

```bash
cf login -a api.fr.cloud.gov --sso
```

Then target the appropriate org and space by following the instructions.

Then push the app, creating the service first:

```bash
cf create-service <service> <service-tag>
#wait a few minutes for the service to be provisionned
cf create-service-key <service-tag> <service-key-name>    #if this returns an OK, then your service has been provisioned  
cf push srt-fbo-scraper --docker-image csmcallister/fbo-scraper
cf bind-service srt-fbo-scraper <service-tag>  
cf restage srt-fbo-scraper
```  

Above, `<service>` is the name of a postgres service (e.g. `aws-rds shared-psql`) while `<service-tag>` is whatever you want to call this service.

Since services can sometimes take up to 60 minutes to be provisioned, we use `cf create-service-key` to ensure the service has been provisioned. See [this](https://cloud.gov/docs/services/relational-database/) for more details.

## Logs
We don't do anything special with logging. We simply write them to STDOUT/STDERR and use https://login.fr.cloud.gov/login to view and search them.

A TODO is logging in JSON using [python-json-logger](https://github.com/madzak/python-json-logger). This will make the logs more easily searchable.

## Contributing

Please read [CONTRIBUTING](https://github.com/GSA/fbo-scraper/blob/master/.github/CONTRIBUTING.MD) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the Creative Commons Zero v1.0 Universal License - see the [LICENSE](https://github.com/GSA/fbo-scraper/blob/master/.github/LICENSE) file for details

## Acknowledgments
 - The [Federal Service Desk](https://www.fsd.gov/fsd-gov/home.do) for answering some of our questions about when the FTP is refreshed
 - The progenitor of this project, which can be found [here](https://github.com/jtexnl/FBOProcurementScan)
 - The [supercronic project](https://github.com/aptible/supercronic)
 - Meshcloud's [example](https://github.com/Meshcloud/cf-cron) of using supercronic within Cloud Foundry
