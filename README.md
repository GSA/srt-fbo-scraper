[![Known Vulnerabilities](https://snyk.io/test/github/GSA/srt-opportunity-gatherer/badge.svg)](https://snyk.io/test/github/GSA/opportunity-gatherer)
[![Maintainability](https://api.codeclimate.com/v1/badges/08f7d22760fe258970d3/maintainability)](https://codeclimate.com/github/GSA/opportunity-gatherer/maintainability)

# srt-opportunity-gatherer (AKA Smartie)

This project gathers Information Technology (IT) solicitations that are posted by the US Federal Government on beta.sam.gov. For each solicitation, we extract the text of each document and feed it to a [supervised machine learning model](https://github.com/GSA/srt-ml) in order to determine whether or not the document contains appropriate [setion 508 accessibility](https://www.section508.gov/) language.

Following a [service-oriented architecture](https://en.wikipedia.org/wiki/Service-oriented_architecture), this project comprises a portion of the back-end for the [Solicitation Review Tool](https://github.com/GSA/srt-ui), a web application that GSA policy experts will use to review IT solicitations for Section 508 compliance; notify deficient solicitation owners; monitor changes in historical compliance; and validate predictions to improve the machine-learning model's performance.

This application is designed to be run as a cron daemon within a Docker image on [cloud.gov](https://cloud.gov/). This is tricky to achieve, as traditional cron daemons need to run as root and have opinionated defaults for logging and error notifications. This usually makes them unsuitable for running in a containerized environment. So, instead of a system cron daemon, we're using [supercronic](https://github.com/aptible/supercronic) to run a dockerized crontab. 

Here's what happens every time the job is triggered:
 1. Fetches yesterday's updated/posted solicitations from beta.sam.gov using the [Opportunity Management API](https://open.gsa.gov/api/opportunities-api/#get-list-of-opportunities), filtering out solictations that don't possess an IT-related [NAICS](https://www.census.gov/eos/www/naics/) code.
 2. Uses the [Federal Hierachy API](https://open.gsa.gov/api/fh-fouo-api/) to lookup canonical agency and office names. 
 3. For each solicitation, downloads a zip archive containing all the solicitation's relevant documents using the [Opportunity Management API](https://open.gsa.gov/api/opportunities-api/#download-all-attachments-as-zip-for-an-opportunity)
 4. Extracts the text from each of those documents using [textract](https://github.com/deanmalmgren/textract).
 5. Restructures the data and inserts it into a PostgreSQL database.
 6. In a future release, the script will poll the database for the number of user-validated predictions on document compliance. If there's a significant increase, those newly validated documents will be sent to the [machine learning component](https://github.com/GSA/srt-ml) of the application to train a new and improved model.
    

## Getting Started

This application is designed to work as a dockerized daemon in cloud.gov. As a cloud.gov app, it's bound with a postgres database that's provided as a brokered service. See the **Deployment** section below if you wish to get started that way.

If you wish to run the application locally, you'll need to perform some setup as we haven't yet configured a docker image that gets this up an running locally.

### Local Setup

Local setup requires:
 - Python 3.6.6
 - PostgreSQL 9.6.8 (newer versions are likely fine)

 Once you've got the above prerequisites met, you'll need to install several OS-specific dependencies to get Python's `textract` library to work. This library is responsible for extracting the text from the myriad solicitation documents. It does so by calling several different OS-specific packages. See their [documentation](https://textract.readthedocs.io/en/stable/installation.html) for more details on the packages you'll need to install given your OS.

#### Local Implementation

Now that you have Python, PostgreSQL, and the textract dependencies, you can run the scan locally within a virtual environment (using [venv](https://docs.python.org/3.6/library/venv.html)). Doing so will create a database with the following connection string: `postgresql+psycopg2://localhost/test`. Make sure postgres is already running in the background and accepting connections on localhost.
 
> By default, the database will persist after the scan, so be sure to drop it using `dropdb test` if you want to clean up afterwards.

To run the scan locally, do the following:

```bash
cd path/to/this/locally/cloned/repo
python3 -m venv env
source env/bin/activate
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

To push to cloud.gov or interact with the app there, you'll need a [cloud.gov account](https://cloud.gov/docs/getting-started/accounts/).

Assuming you've got a cloud.gov account and access to either the application's org or an org of your own, you can login with:

```bash
cf login -a api.fr.cloud.gov --sso
```

Once you're logged in, target the appropriate org and space by following the prompts.

Once you're in the correct space, you can push the app. We do so below, assuming that you haven't already created a postgres service:

```bash
cf create-service <service> <service-tag>
#wait a few minutes for the service to be provisioned
cf create-service-key <service-tag> <service-key-name>    #if this returns an OK, then your service has been provisioned  
cf push srt-opportunity-gatherer --docker-image <your-dockerhub-username>/srt-opportunity-gatherer
cf bind-service srt-opportunity-gatherer <service-tag>  
cf restage srt-opportunity-gatherer
```  

Above, `<service>` is the name of a postgres service (e.g. `aws-rds shared-psql`) while `<service-tag>` is whatever you want to call this service.

>Since services can sometimes take up to 60 minutes to be provisioned, we use `cf create-service-key` to ensure the service has been provisioned. See [this](https://cloud.gov/docs/services/relational-database/) for more details.

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
