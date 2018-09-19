# Table of contents

1. [Branches](#branches)
2. [Commits](#commits)
    1. [Messages](#messages)
3. [Merging](#merging)
4. [Rebasing](#rebasing)

## Branches

* Choose *short* and *descriptive* names:

  ```shell
  # good
  $ git checkout -b xml-to-json

  # bad - too vague
  $ git checkout -b data_fix
  ```

* It's also a fine idea to use issue #'s in the branch name. For example:

  ```shell
  # GitHub issue #15
  $ git checkout -b issue-15
  ```

* Use *hyphens* to separate words.

* When several people are working on the *same* feature, it might be convenient
  to have *personal* feature branches and a *team-wide* feature branch.
  Use the following naming convention:

  ```shell
  $ git checkout -b feature-a/master # team-wide branch
  $ git checkout -b feature-a/maria  # Maria's personal branch
  $ git checkout -b feature-a/nick   # Nick's personal branch
  ```

  Then you can [merge](https://git-scm.com/docs/git-merge) the personal branches into the team-wide branch (see ["Merging"](#merging)).
  Eventually, the team-wide branch will be merged to "master".

* Delete your branch from the upstream repository after it's merged, unless
  there is a specific reason not to.

  Tip: Use the following command while being on "master", to list merged
  branches:

  ```shell
  $ git branch --merged | grep -v "\*"
  ```

## Commits

* Each commit should be a single *logical change*. Don't make several
  *logical changes* in one commit. For example, if a patch fixes a bug and
  optimizes the performance of a feature, split it into two separate commits: one for the bug fix and another for the optimization.

  *Tip: Use `git add -p` to interactively stage specific portions of the
  modified files.*

* Don't split a single *logical change* into several commits. For example,
  the implementation of a feature and the corresponding tests should be in the
  same commit.

* Commit *early* and *often*. Small, self-contained commits are easier to
  understand and revert when something goes wrong.

* Commits should be ordered *logically*. For example, if *commit X* depends
  on changes done in *commit Y*, then *commit Y* should come before *commit X*.

Note: While working alone on a local branch that *has not yet been pushed*, it's
fine to use commits as temporary snapshots of your work. However, you should apply all 
of the above *before* pushing.

### Messages

* Use the editor, not the terminal, when writing a commit message:

  ```shell
  # good
  $ git commit

  # bad
  $ git commit -m "Quick fix"
  ```

  When using `git commit` without the `-m` flag, an editor will open allowing you to
  type a required **subject line** as well as an optional **commit message body**.

#### Subject Line
 * Start your subject line with one of these common prefixes:
    - ENH: Enhancement, new functionality
    - BUG: Bug fix
    - DOC: Additions/updates to documentation
    - TST: Additions/updates to tests
    - BLD: Updates to the build process/scripts
    - PERF: Performance improvement
    - CLN: Code cleanup
  * If applicable, include a reference to the issue within parentheses, using GH1234 or #1234
  * Less than 80 chars
  * Here's an example:
    `ENH: Convert xml to json and write to disk (#3)`

#### Commit Message Body (Optional)
 * Inlcude one blank line
 * Write your commit message.

## Merging
You rebase or merge when you want to integrate changes from one branch into another branch. The difference
between these two operations is htat `git rebase` is destructive whereas `git merge` is not. There's
a great tutorial on these two operations [here](https://www.atlassian.com/git/tutorials/merging-vs-rebasing).

A common `git merge` use-case is when you want to integrate into your branch changes that have happened to master.

To do this, you need to “merge upstream master” in your branch:
  ```
  git checkout shiny-new-feature
  git fetch upstream
  git merge upstream/master
  ```
## Rebasing  
You might need to `git rebase` when you've made a pull request, received a review sometime later, and then had the PR
approved. In this case, you might has a "stale" PR - changes could have happened to `master` that aren't reflected in 
your approved branch. This [tutorial](https://github.com/edx/edx-platform/wiki/How-to-Rebase-a-Pull-Request) walks you 
through rebasing.
