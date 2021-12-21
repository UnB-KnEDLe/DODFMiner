# Contributing Guide  

## How to contribute?

To contribute with this project, you just need to follow the steps up next


* *Fork* of the repository (for external users only)
* Create [branchs](CONTRIBUTING.md#branch-policy)
* Follow the [commits policy](CONTRIBUTING.md#commits-policy)
* Submit [Pull Request](CONTRIBUTING.md#merges-policy-and-pull-requests)


## Branch Policy  

### **main**

The **main** branch is the production branch, where the stable version of the project will be. It will be blocked for commits and pushs.
See the merges policy in the topic [Merges to **main**](CONTRIBUTING.md#merges-to-main).

### **development**

The **dev** branch is where the work of the other branches will be unified and where a stable version will be created to merge with **main**.
Like **main** it is blocked for commits and pushs.
See the merges policy in the topic [Merges for dev] (CONTRIBUTING.md#merges-for-development) merges to **dev** </a>.

### Branch name  

The feature development branches will be created from the **dev** branch with the default nomenclature `change_name`.

## Commits Policy

Commits must be made using the `-s` parameter to indicate your signature on the commit.

```
git commit -s
```

Also, for double commits the `-s` command must be used, and the signature of your pair must be added.

The commit comment must be in english and show the action taken, or the change made.

Comment of commit:
```
Making contribution guide

Change detail

Signed-off-by: Isaque Alves <isaquealvesdl@gmail.com>
Signed-off-by: Felipe Campos <fepas.unb@gmail.com>
```

In order for both involved in the commit to be included as contributors in the GitHub commits graph, just include the statement `Co-authored-by:` in the message:

```
Making contribution guide

Signed-off-by: Isaque Alves <isaquealvesdl@gmail.com>
Signed-off-by: Felipe Campos <fepas.unb@gmail.com>

Co-authored-by: Isaque Alves <isaquealvesdl@gmail.com>
Co-authored-by: Felipe Campos <fepas.unb@gmail.com>

```

For commits that include a small change that has already been resolved, start the commit message with `HOTFIX <message>`

Example of a commit comment:

```
HOTFIX Updating project contribution guide
```

## Merges and Pull Requests Policy

### Pull Requests

Pull requests must be made to the **dev** branch following the rules and steps in the topic [**Merges**](CONTRIBUTING.md#merges). In the pull request content there should be a clear description of what was done.


#### Work in Progress

If there is a need to update the **main** branch before completing the issue, the name of the pull request must contain WIP: <ran_name> so that the branch is not deleted.

## Merges
Merges to **main** should be made when the functionality or refactoring is in accordance with the following aspects:
- Functionality or refactoring completed;
- **Build** of Travis passing;
- Progress or maintain the percentage of test coverage;
- Functionality reviewed by some other member.

To merge into **main** the steps to be followed are:
- `git checkout branch_of_work`;
- `git pull --rebase origin main`;
- `git push origin branch_of_work`;
- Open pull request via GitHub interface;
- Wait for Code Review


### Code Review
The code review must be done by one or more team members who did not participate in the changes.
After at least a Code Review, Status Check (Travis, CodeClimate) approval, PullRequest can be accepted;

To accept PullRequest, you must use the **merge** option on Github.


## Test Coverage

Code coverage is constantly evaluated and the goal is that it never decreases. "Tested code generates less rework and more quality of life".

