# FBO System Documentation
This documentation organizes the disparate sources of official documentation on the FBO System.

It pulls primarily from the [Web Services API documentation](https://www.fbo.gov/downloads/fbo_web_services_technical_documentation.pdf) 
and from the [FBO Electronic Interface Overview](https://www.fbo.gov/?&static=interface).

## Weekly versus Daily Files
Although there's nothing in the official documentation to differentiate the weekly and daily files, the following information
was gleaned from the [Federal Service Desk](https://fsd.gov/fsd-gov/answer.do?sysparm_kbid=f8d0e67e6f585100211956532e3ee402&sysparm_search=).
### Weekly Files
The weekly file is pure XML and contains all **active** opportunities. I can be accessed via FTP here: `ftp://ftp.fbo.gov/datagov/FBOFullXML.xml`

### Daily Files
Each daily file shows the changes during the reporting period (i.e. today's date is for yesterday's changes).  The original 
notice and all modifications to archived notices are posted on one of the FTP feed files at some point in time.
The base url is `ftp://ftp.fbo.gov/`. The naming convention is `FBOFeedYYYYMMDD`, e.g. `ftp://ftp.fbo.gov/FBOFeed20110125`.

## Notice Types and Document Templates
There's a number of **notice types** within FBO (i.e. presolicitation, combined/synopsis, award, etc). The FBO data 
exchange protocol is based on a set of formatted, tagged document templates, each of which represents a specific notice type. 
These are the fifteen (15) templates:
 - Presolicitation Notice - Synopsis
 - Combined Synopsis/Solicitation
 - Amendment to a Previous Combined Solicitation
 - Modification to a Previous Base Notice
 - Award Notice
 - Justification and Approval (J&A)
 - Intent to Bundle Requirements (DoD Funded)
 - Fair Opportunity / Limited Sources Justification
 - Sources Sought Notice
 - Foreign Government Standard
 - Special Notice
 - Sale of Surplus Property
 - Document Upload
 - Document Deleting
 - Document Archival
 - Document Unarchival
 
Metadata for each of these templates can be found [here](https://www.fbo.gov/?&static=interface). These docs specify the
XML tags for each notice template.
 
## Attachments
Some of the templates have tags (e.g. `<URL>`) that provide a link to additional documentation.
 
## Valid Tag Values
Occasioanlly, the documentation lists the valid values for a tag. We'll document those here.

### Set-Aside Values
Valid tag values include:
 - 'N/A'
 - ‘Competitive 8(a)’
 - ‘Emerging Small Business’
 - 'HUBZone'
 - 'Partial HBCU / MI'
 - 'Partial Small Business'
 - 'Service-Disabled Veteran-Owned Small Business'
 - 'Total HBCU / MI'
 - 'Total Small Business'
 - 'Veteran-Owned Small Business'
 - ‘Woman Owned Small Business’
 - ‘Economically Disadvantaged Woman Owned Small Business’
