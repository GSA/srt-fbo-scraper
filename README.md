# fbo-scraper aka smartie!
[FBO](https://www.fbo.gov/) is the U.S. government's system of record for opportunities to do business with the government. Every week, the FBO system posts all active opportunities as an xml file that is made publically available via the File Transfer Protocol (FTP), which is a standard network protocol used for the transfer of computer files between a client and server on a computer network.

This project downloads the xml of a weekly FBO file and converts it to JSON. Eventually, we'll scan opportunities for compliance with various Federal policies. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This project relies on Python 3.6. It only uses standard libraries, so you shoud be able to use Python >= 2.6. Note that if you're using Python 2.x, you'll probably receive this error

```
import json, urllib.request

ImportError: No module named request
```

To get things working in Python 2.x, you need to change the import statement to:

```
from urllib2 import urlopen
```
and then use `urlopen(url)` instead of `urllib.request.urlopen(url)`.

### Installing

For now, you just need to be sure you have Python. To run the script, it's as easy as:

```
$ python fbo_weekly_scraper.py
```
That will download and write the xml. It will also conver the xml to JSON and write that as well. Each file is roughly 1.7GB

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
