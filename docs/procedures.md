# SRT Procedures

This document codifies internal project procedures related to the application's System Security Plan and System Lifeclye Management.

## Account Management & System Access

In this section, we document our account management processes for the SRT GitHub repositories and cloud.gov organizationin. We also document our process for remote access to the SRT application itself.

The SRT System Administrator will review accounts for compliance with account management requirements annually.

### GitHub Access 

The System Administrator and current project developers need commit rights to this repository.  The system owner manages this access, granting access to new project developers when they come onboard and removing access when they leave.  
  
Both of the adding and removing processes should be initiated by creating an issue in the project's [issue tracker](https://github.com/GSA/srt-fbo-scraper/issues).  Any one can create the issue, but the system owner should be the one who addresses and closes it.  

These accounts are created for developers that need access to contribute code and deploy apps.

1. [Create an account](https://github.com/) with GitHub and [enable multi factor authentication](https://github.com/blog/1614-two-factor-authentication).
2. Make sure you have [gitseekrets](https://github.com/18F/laptop/tree/master/seekret-rules) installed whereever you develop.
3. Then, you will want to contact the system owner by creating a new issue in the [issue tracker](https://github.com/GSA/srt-fbo-scraper/issues). In that message, include your name, the name of your supervisor, confirm you have two-factor authentication on and have installed gitseekrets. 
4. The system owner will confirm the GSA identity of the applicant, and signal approval in the ticket. 
5. The system owner will then add the GitHub handle for the new member to the GSA GitHub team and close the ticket.


### Cloud.gov Access 

The SRT System Administrator posseses the following three roles at the organization level:
 - Org Manager: Administer the org.
 - Org Auditor: Read-only access to user information and org quota usage information.
 - Org Billing Manager: Create and manage billing account and payment information.

Project developers will need cloud.gov access to the `gsa-ogp-srt` org. The System Administrator manages this access, granting access to new project developers when they come onboard and removing access when they leave.  

Specifically, developers are [granted](https://cloud.gov/docs/apps/managing-teammates/) OrgManager rights to the `gsa-ogp-srt` org and SpaceDeveloper rights to each of the project's spaces.  

Both of the adding and removing processes should be initiated by creating an issue in the project's [issue tracker](https://github.com/GSA/srt-fbo-scraper/issues). Anyone can create the issue, but the system owner should be the one who addresses and closes it.

These accounts are created primarily for developers that need access to contribute code and debug apps. Users are assigned to the appropriate logical roles from the following list:
* Developer/QA - Users in this role are assigned to the cloud.gov 'Space Developer' role in the dev and staging spaces
* System Administrator - Users in this role are assigned to the cloud.gov 'Space Developer' role in the dev, staging, and production spaces
* System Owner - Users in this role are assigned to the cloud.gov 'Space Developer' role in the dev, staging, and production spaces. Additionally, users in this role will be marked as 'Org Managers' for the gsa-ogp-srt organization on cloud.gov.

Before opening an issue to request access, follow these steps:

1. [Create a github account](https://github.com/) that abides by GSA's GitHub account-creation [rules](https://github.com/GSA/GitHub-Administration).

2. Make sure you have [gitseekrets](https://github.com/18F/laptop/tree/master/seekret-rules) installed wherever you develop.

3. Contact the system owner by creating a new issue in the [issue tracker](https://github.com/GSA/srt-fbo-scraper/issues). In that message, include your name, the name of your supervisor, confirm that you have two factor authentication on and have installed gitseekrets. 

4. The system owner will confirm the GSA identity of the applicant and comment on the ticket to show approval. 

5. The system owner will invite the person to cloud.gov. Once they accept the invite, the system owner will add that person to the organization and appropriate spaces within cloud.gov. 
 
6. The issue history will document the role that was assigned.

### Remote Access
The SRT application can only be accessed through the cloudfoundry CLI. This requires a cloud.gov account as well as appropriate user roles, which were outlined above.

Instructions for installing the cloudfoundry CLI can be found [here](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html). Documentation can be found [here](https://docs.cloudfoundry.org/cf-cli/cf-help.html). We've also enabled SSH access via the CLI tool, and you can read more about that [here](https://docs.cloudfoundry.org/devguide/deploy-apps/ssh-apps.html).


## Weekly Monitoring Checklist

The development team checks for security events weekly. Any unusual or suspicious activities are immediately brought to the team's attention in the project slack channel (#md-fbo-scraper) and the system owner coordinates appropriate investigation and followup. The team will follow the [18F incident response handbook](https://handbook.18f.gov/security-incidents/), which aligns with GSA policy.

Checklist:
1. Create an issue in the project's [issue tracker](https://github.com/GSA/srt-fbo-scraper/issues) to track this Security Event Review.
2. Review project's [Snyk](https://snyk.io/test/github/GSA/srt-fbo-scraper) and open a ticket for all "red" alerts.
3. Review [production logs](https://logs.fr.cloud.gov) for unapproved and unusual activities. 
4. Review actionable security events on production logs for successful and unsuccessful account logon events, account management events, object access, policy change, privilege functions, process tracking, system events, all administrator activity, authentication checks, authorization checks, data deletions, data access, data changes, and permission changes.
5. Deactivate any cloud.gov and github access when people who have left the team; when accounts are no longer required; when users are terminated or transferred; and when individual information system usage or need-to-know changes.
6. Note any findings in an issue.
7. Work on and close the issue.

## Audit Processing Failure Policy

We rely on cloud.gov’s [audit tool](https://logs.fr.cloud.gov).  In the event of an audit processing failure, their [contingency plan](https://cloud.gov/docs/ops/contingency-plan/) stipulates that they’ll notify the SRT system owners. If we receive a notification from cloud.gov about an temporarily irremediable issue with the audit tool, we'll  shutdown SRT until the issue has been resolved. 

## Unsupported System Components Policy
At present, there are no unsupported components in the SRT system. If currently-used components become deprecated and/or unsupported, we will bump their versions to the most recent stable release. If we're unable to make those bumps, then we will provide justification and document approval for the continued use of the unsupported system components within the relevant GitHub issue.
