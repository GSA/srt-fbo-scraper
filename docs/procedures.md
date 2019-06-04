This document codifies internal project procedures related to the application's System Security Plan.

### Cloud.gov Access 

The System owner and current project developers need cloud.gov access to the `gsa-ogp-srt` org.  The system owner manages this access, granting access to new project developers when they come onboard and removing access when they leave.  

Specifically, current developers are [granted](https://cloud.gov/docs/apps/managing-teammates/) OrgManager rights to `gsa-ogp-srt` and SpaceDeveloper rights to each of the projects spaces.  

Both of the adding and removing processes should be initiated by creating an issue in the project's [issue tracker](https://github.com/18F/pulse/issues).  Any one can create the issue, but the system owner should be the one who addresses and closes it.    

These accounts are created for developers that need access to contribute code and debug apps.

1. [Create an account](https://github.com/) with cloud.gov and this will include multi factor authentication with [Google authenticator](https://support.google.com/accounts/answer/1066447?hl=en) or [authy](https://www.authy.com/).

2. Make sure you have [gitseekrets](https://github.com/18F/laptop/tree/master/seekret-rules) installed wherever you develop.

3. Then, you will want to contact the system owner by creating a new issue in the [issue tracker](https://github.com/GSA/srt-fbo-scraper/issues).  In that message, include your name, the name of your supervisor, confirm you have two factor authentication on and have installed gitseekrets. 

4. The system owner will confirm the GSA identity of the applicant and comment on the ticket to show approval. 

5. The system owner will add a person to the organization in cloud.gov. 
 
6. The issue history will document the role that was assigned.

### GitHub Access 

The System owner and current project developers need commit rights to this repository.  The system owner manages this access, granting access to new project developers when they come onboard and removing access when they leave.  
  
Both of the adding and removing processes should be initiated by creating an issue in the project's [issue tracker](https://github.com/GSA/srt-fbo-scraper/issues).  Any one can create the issue, but the system owner should be the one who addresses and closes it.  

These accounts are created for developers that need access to contribute code and deploy apps.

1. [Create an account](https://github.com/) with GitHub and [enable multi factor authentication](https://github.com/blog/1614-two-factor-authentication).
2. Make sure you have [gitseekrets](https://github.com/18F/laptop/tree/master/seekret-rules) installed whereever you develop.
3. Then, you will want to contact the system owner by creating a new issue in the [issue tracker](https://github.com/GSA/srt-fbo-scraper/issues). In that message, include your name, the name of your supervisor, confirm you have two-factor authentication on and have installed gitseekrets. 
4. The system owner will confirm the GSA identity of the applicant, and signal approval in the ticket. 
5. The system owner will then add the GitHub handle for the new member to the GSA GitHub team and close the ticket.

### Weekly Monitoring Checklist

The development team checks for security events weekly. Any unusual or suspicious activities are immediately brought to the team's attention in the project slack channel (#md-fbo-scraper) and the system owner coordinates appropriate investigation and followup. The team will follow the [18F incident response handbook](https://handbook.18f.gov/security-incidents/), which aligns with GSA policy.

Checklist:
1. Create an issue in the project's [issue tracker](https://github.com/GSA/srt-fbo-scraper/issues) to track this Security Event Review.
2. Review project's [CodeClimate](https://codeclimate.com/github/GSA/srt-fbo-scraper) and open a ticket for all "red" alerts.
3. Review [production logs](https://logs.fr.cloud.gov) for unapproved and unusual activities. 
4. Review actionable security events on production logs for successful and unsuccessful account logon events, account management events, object access, policy change, privilege functions, process tracking, system events, all administrator activity, authentication checks, authorization checks, data deletions, data access, data changes, and permission changes.
5. Deactivate any cloud.gov and github access for people who have left the team.
6. Note any findings in an issue.
7. Work on and close the issue.
