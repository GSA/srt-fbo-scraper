[![CircleCI](https://circleci.com/gh/GSA/fbo-scraper/tree/master.svg?style=svg)](https://circleci.com/gh/GSA/fbo-scraper/tree/master)
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
There are two docker images for this project:  [fbo-scraper](https://cloud.docker.com/u/csmcallister/repository/docker/csmcallister/fbo-scraper) and [fbo-scraper-test](https://cloud.docker.com/u/csmcallister/repository/docker/csmcallister/fbo-scraper-test). The former contains the application that can be pushed to cloud.gov (see below) while the latter is strickly for testing during CI.

### Prerequisites
Anyone can download the docker images and tinker around. To push to cloud.gov, you'll need a [cloud.gov account](https://cloud.gov/docs/getting-started/accounts/). You can also run it locally so long as you have postgres installed.


## Running the tests
To run the tests:

`$ python -W ignore -m unittest test.py`

Several warnings and exceptions will print out. Those are by design as they're being mocked in the tests.


## Deployment
Below, `<service>` is the name of your postgres service of choice (e.g. `shared-psql`) while `<service-tag>` is whatever you want to call it.
```
$ cf create-service <service> <service-tag>  
$ cf create-service-key <service-tag>     *this may take a few minutes to configure*  
$ cf push srt-fbo-scraper --docker-image csmcallister/fbo-scraper
$ cf bind-service srt-fbo-scraper <service-tag>  
$ cf restage srt-fbo-scraper
```  

## Contributing

Please read [CONTRIBUTING](https://github.com/GSA/fbo-scraper/blob/master/.github/CONTRIBUTING.MD) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the Creative Commons Zero v1.0 Universal License - see the [LICENSE](https://github.com/GSA/fbo-scraper/blob/master/.github/LICENSE) file for details

## Acknowledgments
 - The [Federal Service Desk](https://www.fsd.gov/fsd-gov/home.do) for answering some of our questions about when the FTP is refreshed
 - The progenitor of this project, which can be found [here](https://github.com/jtexnl/FBOProcurementScan)
 - The [supercronic project](https://github.com/aptible/supercronic)
 - Meshcloud's [example](https://github.com/Meshcloud/cf-cron) of using supercronic within Cloud Foundry
