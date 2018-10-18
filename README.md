# fbo-scraper
[FBO](https://www.fbo.gov/) is the U.S. government's system of record for opportunities to do business with the government. Each night, the FBO system posts all _updated_ opportunities as a pseudo-xml file that is made publically available via the File Transfer Protocol (FTP), which is a standard network protocol used for the transfer of computer files between a client and server on a computer network.

This project downloads that pseudo-xml and converts it to JSON. It then scrapes all of the notice attachment urls from each notice's official FBO url. Then it extracts the text from those documents (where possible). Finally, it feeds that text into a binary classifier to predict whether or not the document is 508 accessibility compliant. The classifier was built and binarized using `sklearn` based on approximately 1,000 hand-labeled solicitations.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
This project relies on Python 3.6. We'll soon have a complete `requirements.txt` and set-up script to get you going with all of the dependencies, the biggest of which is `textract`, which is used to extract text from sundry document types (e.g. pdf, docx, doc, rtf).

### Installing

If you cloned the repo and `pip` installed all of the dependencies manually, then :clap:

Now all you need to do to run the program is:

```
$ python fbo.py
```

Runtime depends on how many attachments are in the most recent nightly file. At most expect approximately 30 minutes. Quickest we've seen was just a minute. At present, the program doesn't write any results (but it'll soon include something simple to write results to csv).

## Running the tests

Coming soon!

### And coding style tests

Coming soon! (hopefully PEP8 Speaks)

## Deployment

Coming soon!

## Contributing

Please read [CONTRIBUTING](https://github.com/GSA/fbo-scraper/blob/master/.github/CONTRIBUTING.MD) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the Creative Commons Zero v1.0 Universal License - see the [LICENSE](https://github.com/GSA/fbo-scraper/blob/master/.github/LICENSE) file for details

## Acknowledgments
 - The [Federal Service Desk](https://www.fsd.gov/fsd-gov/home.do) for answering some of our questions about when the FTP is refreshed.
 - The progenitor of this project, which can be found [here](https://github.com/jtexnl/FBOProcurementScan).
