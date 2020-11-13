# SRT Procedures

This document codifies internal project procedures related to the application's System Security Plan and System Lifeclye Management.

## Account Management & System Access

In this section, we document our account management processes for the SRT GitHub repositories and cloud.gov organizationin. We also document our process for remote access to the SRT application itself.

We follow the principle of least privilege (POLP), which is the practice of limiting access rights for users to the bare minimum permissions they need to perform their work.

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

#### Cloud.gov Service Account

Within the application's cloud.gov organization, there's a [service account](https://cloud.gov/docs/services/cloud-gov-service-account/) with the Space Developer role in each space. CircleCI uses these service accounts to deploy the application after PR merges. However, **service account passwords expire after 90 days**, so it's necessary to periodically delete the existing service key, recreate it, and then update the CircleCI environment variables that contain the username/password.

After logging into cloud.gov with your own account and targeting the appropriate space, you can  delete and recreate service keys for a service account with the following:

```bash
cf delete-service-key srt-fbo-scraper-service-account srt-fbo-scraper-service-account-key
cf create-service-key srt-fbo-scraper-service-account srt-fbo-scraper-service-account-key
cf service-key srt-fbo-scraper-service-account srt-fbo-scraper-service-account-key
```

The last command will return the service account username/password pair. Once you have those, navigate to CircleCI to update the environment variables.

### SRT Web Application Access

Individuals wanting to use the SRT Web Application will be approved by the SRT Product Owner (PO). During this approval, the PO will make a determination on the proper role to assign the new user. New users will be assigned roles that have the minimum permissions necessary to carry out their responsibilities. The PO is able to add users to SRT by assigning them to groups on MAX.gov. 

Here is the step-by-step for adding a user to one of the SRT access groups:
* Log into MAX.gov: https://max.gov
* On your MAX user home page you should see a section labeled Collaboration Groups. In that section, find the group you want to put the new user in. This will typically be SRT-508-COORDINATOR for 'regular' SRT users. In the associated dropdown list, choose the "Manage Group" action
* On the manage group page you can see the list of current members. If the user is not listed already, click the "Add Users" button.
* On this page you can search fro the appropriate user by name or email address. Click Check Email Addresses when done.
* When the email addresses have been verfified, the confirmation page will show the invitation text that will be sent by email. You can either modifiy the text or uncheck the Notify Users with MAX Accounts check box.
* Click the Send Invitations button to finish the process.


### Remote Access

The SRT application can only be accessed through the cloudfoundry CLI. This requires a cloud.gov account as well as appropriate user roles, which were outlined above.

Instructions for installing the cloudfoundry CLI can be found [here](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html). Documentation can be found [here](https://docs.cloudfoundry.org/cf-cli/cf-help.html). We've also enabled SSH access via the CLI tool, and you can read more about that [here](https://docs.cloudfoundry.org/devguide/deploy-apps/ssh-apps.html).

### Database Updates & Migrations

We use [SQLAlchemy](https://docs.sqlalchemy.org/en/13/) to model our PostgreSQL database's schema and [alembic](https://alembic.sqlalchemy.org/en/latest/) to handle migrations. Although the client-side of the SRT also uses a tool similar to SQLAlchemy to model the database, migrations and updates should occur through this application.

#### Updates

Although you *could* use alembic to update stored data values, that can sometimes be impractical. In those cases, you can develop a script locally and use `cf ssh` piped with `cat` to transfer a local file into the app's space. Assuming you've already logged in via the cf CLI and have targeted a space, you could accomplish this with:  

```bash
cat local_file_path.py | cf ssh MY-AWESOME-APP -c “cat > remote_file_path.py”
```

With the file piped into your app, you can then use `cf ssh MY-AWESOME-APP` to get in. From there, you'll need to update your `PATH` to use a version of Python that has access to the project's dependencies. You can do that with:

```bash
PATH=/usr/local/bin:$PATH
```

From there, you can execute your update script:

```bash
python3 remote_file_path.py
```

And cleanup after:

```bash
rm remote_file_path.py
```

#### Migrations

For schema updates, you need to use `alembic` to perform a migration. This project already has a configured alembic environment, so you can follow the directions [here](https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script) to create a migration script.

Once you've tested your migration, you can then prepend the [crontab](https://github.com/GSA/srt-fbo-scraper/blob/master/crontab) command with `alembic upgrade head` so that the migration occurs with the next cron job before the script is itself executed.

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

## GSA Solutions Life Cycle (SLC)

The primary objectives of an SLC are to deliver quality systems that: meet or exceed customer expectations when promised and within cost estimates; work effectively and efficiently within the current and planned information technology (IT) infrastructure; and are inexpensive to maintain and cost-effective to enhance.

The SRT System Administrator assumes all information security roles and responsibilities throughout the SLC.

The SRT Team integrates the organizational information security risk management process into the system development life cycle activities documented here.

The SLC is comprised of nine phases. Here we documented how the Solicitation Review Tool (SRT) is managed via SLC.

### Phase One – Solution Concept Development

The initiation of a solution (system or application) project begins when a business need or opportunity is identified. In this phase, we identified a need for increase the number of Federal ICT solicitations being checked for compliance with accessibility requirements as defined in Section 508 of the Rehabilitation Act.

### Phase Two - Planning

This phase is concerned with how the business will operate once the approved solution (i.e. SRT) is implemented, and to assess how the solution will impact employees and customers, including impacts on their privacy. Our team has engaged with section-508 coordinators accross the 24 CFO-Act agencies in order to collect user stories, conduct user acceptance testing, and to validate the accuracy of the compliance classifications rendered by the machine learning algorithms.

### Phase Three – Requirements Analysis

In this phase, the SRT team collected functional user requirements and formally defined them in terms of data, solution performance, security, and maintainability in light of resource contraints.

### Phase Four – Design

In this phase, our team designed the physical characteristics of the SRT system given the requirements delineated in the previous phase.

### Phase Five – Development

In this phase, the SRT Team produced translated the detailed specifications enumerated in the design phase into executable software created through incremental development techniques in intervals that were not to exceed six months. All software components were unit tested, integrated, and re-tested in a systematic manner using CircleCI in conjuction with GitFlow.

### Phase Six – Integration and Testing

In this phase, the various components of the solution were integrated and systematically tested in a development environment within cloud.gov. Prospective users also began to test the solution to ensure that the functional requirements are satisfied. Prior to operating in a production environment, the solution will undergo certification and accreditation activities that include system testing, regression testing, test plan, test scripts, and user acceptance testing.

### Phase Seven – Implementation

In this phase, SRT will be pushed to a production environment in cloud.gov. This phase is initiated only after the SRT has been tested and accepted by the test users and received an Authority to Operate (ATO) from GSAIT.

### Phase Eight – Operations and Maintenance

We intend SRT operations to be ongoing. As such, SRT will be monitored for continual performance in accordance with user requirements. Needed solution modifications will be requested through GitHub issues made if deemed appropriate by the SRT Team. The operational solution is also periodically assessed through in-process reviews and post implementation reviews to determine how the solution can be made more efficient and effective. The continuation or ongoing investment of the solution will be reviewed during the annual IT budget formulation (zero-based budget) process. During this time, governance groups (senior agency leaders) have the option to continue or halt funding, based on performance. Investments or projects can also be reviewed periodically (outside of budget formulation) as risks arise or other trigger factors require leadership escalation. Operations will continue as long as the solution can be effectively adapted to respond to an organization’s needs. Lastly, when necessary modifications or changes are identified, the solution may re-enter the planning phase.

### Phase Nine – Disposition

Disposition activities ensure the orderly termination of the solution and preserve the vital information about the solution so that some or all of the information may be reactivated in the future, if necessary. Particular emphasis is given to proper preservation of the data processed by the solution, so that the data is effectively migrated to another solution or archived, in accordance with applicable records management regulations and policies, for potential future access. We use GitHub to archive the codebase and will backup the database (if deemed necessary) as a separate AWS RDS instance.
