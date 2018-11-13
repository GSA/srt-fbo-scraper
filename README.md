# fbo-scraper (AKA Smartie)
[FBO](https://www.fbo.gov/) is the U.S. government's system of record for opportunities to do business with the government. Each night, the FBO system posts all _updated_ opportunities as a pseudo-xml file that is made publically available via the File Transfer Protocol (FTP), which is a standard network protocol used for the transfer of computer files between a client and server on a computer network.

This project uses supervised machine learning to determine whether or not the solicitation documents of Information Communications Technology (ICT) notices contain appropriate [setion 508 accessibility](https://www.section508.gov/) language.

Following a [service-oriented architecture](https://en.wikipedia.org/wiki/Service-oriented_architecture), this repository, along with a forthcoming API, will provide a back-end to a UI that GSA policy experts will use to review ICT solicitations for 508 compliance; notify deficient solicitation owners; monitor changes in historical compliance; and validate predictions to improve model performance.

The application is designed to be run as a cron daemon within [cloud.gov](https://cloud.gov/). This is tricky to achieve as traditional cron daemons need to run as root and have opinionated defaults for logging and error notifications. This makes them unsuitable for running in a containerized environment like Cloud Foundry. So, instead of a system cron daemon, we're using [supercronic](https://github.com/aptible/supercronic) to run the cron tab. This method is demonstrated without a python script here.


Here's what happens every time the job is triggered:
    1. Download the pseudo-xml from the FBO FTP every day
    2. Convert that pseudo-xml to JSON
    3. Extract solictations from the Information Communications Technology (ICT) categories
    4. Srape each ICT soliticiatons documents from their official FBO urls
    5. Extract the text from each of those documents using [textract](https://github.com/deanmalmgren/textract)
    6. Feed the text of each document into a binary classifier to predict whether or not the document is 508 compliant tThe classifier was built and binarized using [sklearn](https://github.com/scikit-learn/scikit-learn) based on approximately 1,000 hand-labeled solicitations)
    7. Insert data into a postgreSQL database
    8. Retrain the classifer if there is a sufficient number of human-validated predictions in the database (validation will occur via the UI)
    

## Getting Started
This application is built courtesty of the [multi-buildpack](https://github.com/cloudfoundry-attic/multi-buildpack) using the [python-buildpack](https://github.com/cloudfoundry/python-buildpack), [apt-buildpack](https://github.com/cloudfoundry/apt-buildpack), and [binary buildpacks](https://github.com/cloudfoundry/binary-buildpack). The binary buildpack executes supercronic on the crontab file while the apt-buildback handles all of textract's external dependencies, which can be found in `apt.yml`. The crontab file specifies a single cron job, which is to execute `fbo.py`. 

>Note: By default, supercronic logs all output to stderr, so we redirect that to stdout for cf logging purposes in the cf manifest command.


### Prerequisites
This application requires a [cloud.gov account](https://cloud.gov/docs/getting-started/accounts/) as it's not yet configured to run locally. We'll be working on that as well as within an CI environment.


## Running the tests

Coming soon!

### And coding style tests

Coming soon! (hopefully PEP8 Speaks)

## Deployment

cf create-service *service* *plan* smartie_db  
cf create-service-key smartie_db    *this may take a few minutes to configure*  
cf push smartie  
cf bind-service smartie smartie_db  
cf restage smartie  

## Contributing

Please read [CONTRIBUTING](https://github.com/GSA/fbo-scraper/blob/master/.github/CONTRIBUTING.MD) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the Creative Commons Zero v1.0 Universal License - see the [LICENSE](https://github.com/GSA/fbo-scraper/blob/master/.github/LICENSE) file for details

## Acknowledgments
 - The [Federal Service Desk](https://www.fsd.gov/fsd-gov/home.do) for answering some of our questions about when the FTP is refreshed
 - The progenitor of this project, which can be found [here](https://github.com/jtexnl/FBOProcurementScan)
 - The [supercronic project](https://github.com/aptible/supercronic)
 - Meshcloud's [example](https://github.com/Meshcloud/cf-cron) of using supercronic within Cloud Foundry
