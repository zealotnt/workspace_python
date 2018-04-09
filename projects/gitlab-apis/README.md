- Start gitlab-docker-composer: https://github.com/sameersbn/docker-gitlab
- When gitlab ready, update the credential at: `.env` and `gitlab.cfg`
    + My `private_token` can get at: http://localhost:10080/profile/personal_access_tokens
    + Target `private_token` can get at: http://<target-url>/profile/account (running API-v3, 8.8.4 d4c3f17)
- Now clone the `Groups` structure of target to our gitlab-server: `python gitlab-cloner.py`
    + It will ask us if to clear all existing group, we may need yes
    + It will then create the same group of target gitlab to our gitlab

- The `Suggesting cloning URL` also printed
- Clone the repos one by one:
    + New (button at the web-toolbar) -> Dropdown `New project`
    + Tab `Import Project` -> Tab `Repo by URL`
    + Paste the URL at `Suggesting cloning URL`, to `Git repository URL`
    + Change the `Project path` accordingly (the group may not be updated - poor you gitlab), the `Project name` auto detect seems good
    + Click `Create project` -> Done
