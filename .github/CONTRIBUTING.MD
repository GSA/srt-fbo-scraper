# Contributing
We'd love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## We Use [Github Flow](https://guides.github.com/introduction/flow/index.html), So All Code Changes Happen Through Pull Requests
Pull requests are the best way to propose changes to the codebase. If you're a Fed on the team, then you'll follow the The **The Shared Repository Model**. If you're anybody else, you'll follow the **Fork and Pull Model**.

### Commit Guidelines
The following defines how a commit message should be structured. Please reference the relevant GitHub issues in your commit message using GH1234 or #1234. Either style is fine.

 - an appropriately prefixed (see below) subject line with < 80 chars and the relevant issues(s)
 - one blank line.
 - optionally, a commit message body.

For the subject line, we'd prefer it if you prefixed the line with one of these acronyms:

 - ENH: Enhancement, new functionality
 - BUG: Bug fix
 - DOC: Additions/updates to documentation
 - TST: Additions/updates to tests
 - BLD: Updates to the build process/scripts
 - PERF: Performance improvement
 - CLN: Code cleanup

Here's an example:
```bash
git commit -m "TST: add test cases for foo (#1)"
```

## The Shared Repository Model (GSA employees and contractors only)
### Short Version
When you want to work on something, clone the repository and make a new branch for your feature. Prepend the name of the branch with your GitHub username (e.g. `git checkout -b csmcallister-new-feature`). 

As you implement changes, commit them to your local branch. Then, push that branch to the GitHub remote and make a pull request. Format the pull request title to follow the commit guidlines, using the appropriate prefix and referencing the relevant issue(s). Add a message if you think it's needed.

### Long Version
#### Writing your Code
1. `clone` the repository:
```bash
git clone https://github.com/GSA/fbo-scraper.git
```
2. `checkout` a branch for your feature before doing anything (prepend your username):
```bash
git checkout -b csmcallister-shiny-new-feature
```
3. Do some work, staging files you've edited for commit like this:
```bash
git add [file.name]
```
You can `add` one, several, or all modified files. To add all, use a dot:
```bash
git add .
```
4. `commit` those changes to your local branch. Use the `-m` flag if you don't want to include a commit body.
```bash
git commit
```
5. To `push` those commits to the remote repository as a non-master branch, run:
```bash
git push origin shiny-new-feature
```
6. This will create a shiny-new-feature branch in the origin repository, ie. the repository on GitHub.
7. You should now be able to see your branch on the origin repository. To make the Pull Request, click on your branch name. Then, click the "Pull Request" button, either on the top right of the screen, or in the center of the page under the label "Your recently pushed branches:". Click the Send Pull request button and move onto reviewing your code.
 
 #### Reviewing your Code
You can review/comment on pull requests at https://github.com/GSA/fbo-scraper/pulls. 

If your PR failed the tests, or added code that isn't covered by a test, then update/add the code/test(s).

If there's a gray bar saying "This pull request cannot be automatically merged.", then you've got some more work ahead of you. That's because the file(s) that your pull request modifies was/were updated in the meantime. To avoid a conflict on the remote, GitHub won't let you automatically merge into master. This means you need to update your Pull Request by merging the origin's master branch into your feature branch. In short, you need to “merge upstream master” in your branch:

```bash
git checkout shiny-new-feature
git fetch origin
git merge origin/master
```

If there are no conflicts (or they could be fixed automatically), a file with a default commit message will open, and you can simply save and quit this file.

If there are merge conflicts, you'll need to solve those conflicts. See [this](https://help.github.com/articles/resolving-a-merge-conflict-using-the-command-line/) for an explanation on how to do this. Once the conflicts are fixed and merged and the files where the conflicts were solved are added, you can run `git commit` to save those fixes.

If you have uncommitted changes at the moment you want to update the branch with master, you will need to stash them prior to updating (see the [stash docs](https://git-scm.com/book/en/v2/Git-Tools-Stashing-and-Cleaning)). This will effectively store your changes and they can be reapplied after updating.

After your feature branch has been update locally, you can now update your pull request by pushing to the branch on GitHub:
```bash
git push origin shiny-new-feature
```


#### Deleting your Branch
Once your feature branch is accepted, you’ll probably want to get rid of the branch. You can do that to the remote master right within the pull request page. To delete the branch locally, you need to pull the remote master down into your local master. Then git will know it's safe to delete your branch.

```bash
git checkout master
git fetch origin
git merge origin
```

Now that your local master is even with the remote, you can do:
```bash
git branch -d shiny-new-feature
```

> Make sure you use a lower-case -d, or else git won’t warn you if your feature branch has not actually been merged.

## The Fork and Pull Model (all other contributors)
This model is the same as the Shared Repository Model except that you need to first fork this repo. To to this, you go to the project page and hit the Fork button. You will then want to clone your fork to your machine:

```bash
git https://github.com/GSA/fbo-scraper.git yourusername-fbo-scraper
cd yourusername-fbo-scraper
git remote add upstream https://github.com/GSA/fbo-scraper.git
```

This creates the directory yourusername-fbo-scraper and connects your repository to the upstream (main project) repository. Once you've done this, make your branch, write some code, add and commit your changes, push your forked feature branch’s commits, make your pull request, and await review. 

## Any contributions you make will be under the Creative Commons Zero v1.0 Universal
In short, when you submit code changes, your submissions are understood to be under the same Creative Commons License that covers the project.

## Report bugs and make feature requests using Github issues
We use GitHub issues to track bugs and make feature requests. [Open a new issue](https://github.com/GSA/fbo-scraper/issues) if you've got an idea.

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can. 
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style
This might not be strictly enforced, but this is generally a good thing.

## License
By contributing, you agree that your contributions will be licensed under its Creative Commons Zero v1.0 Universal.
