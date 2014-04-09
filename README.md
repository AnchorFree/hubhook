hubhook
=======

A minimalistic github webhook for continuous deployment / integration of code hosted on github.
The current implementation only supports deployments of code to `/srv`.
Extending it would be pretty simple, as would adding a post deploy hook, but...
We don't need that functionality, yet.
Pull requests accepted and appreciated.

Usage
-----

The following example demonstrates how to configure hubhook to continuously deploy it'self.
This is probably overkill, but it will get you started.
The idea is that once you have hubhook running on your server,
you can configure other code for continious deployment.
To add another repo for continious deployment, follow the steps below
using your org and repo instead of AnchorFree and hubhook.

Create deploy keys as user root.

```bash
sudo -i
export REPO_NAME=hubhook
ssh-keygen -b 2048 -C "$REPO_NAME deploy key" -f ~/.ssh/${REPO_NAME}_deploy_key
cat ~/.ssh/~{REPO_NAME}_deploy_key
```

Add the public key to your repository's deploy keys at https://github.com/AnchorFree/hubhook/settings/keys

Modify `/root/.ssh/config` to create aliases that link associate the appropriate deploy keys.
If you are using github enterprise, put your enterprise server's hostname instead of `github.com`.
Note that the LogLevel quiet is critical,
if you skip this GitPython will have problems because of warning messages SSH generates around known hosts.
You may also want to disable `known_hosts` behavior (the last 2 lines have this effect).

```ssh_config
Host git_hubhook
  HostName github.com
  User git
  IdentityFile /root/.ssh/hubhook_deploy_key
  LogLevel quiet
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
```

If you did not disable `known_hosts` you need to populate them using the following command.
If you are working with github.com rather than Github Enterprise you may need to run this several times
so that it can pick up the various ssh endpoints.
All the more reason to disable `known_hosts` behavior.

```bash
ssh git_hubhook
```

Accept the new host. It doesn't hurt to do this either way to verify the ssh keys are working.

Now clone your repository into `/srv`, but use the ssh alias instead of the usual address.

```bash
git clone git_hubhook:AnchorFree/hubhook.git
```

Configure a github webhook to hit the hubhook url at https://github.com/AnchorFree/hubhook/settings/hooks
add url http://myserver:8080/hubhook.py

If you have already installed hubhook and are following this guide to configure hubhook support for another repository,
congratulations, you're done! Testing instruction follow.
If you're working on installing hubhook, skip down to the Create virtualenv step below.

Create the virtual environment.
This assumes you have already installed python, pip and virtualenv support.

```bash
sudo -i
cd /srv
virtualenv hubhook_virtualenv
/srv/hubhook_virtualenv/bin/pip install -r /srv/hubhook/requirements.txt
```

Start up hubhook. This is pretty trivial since we're just using twistd web.
The following command line is includes the `-n` argument to keep it in the foreground, intended for debugging.
You will probably want to use supervisord or circus to make sure this service stays up and running.

```bash
sudo -i
/srv/hubhook_virtualenv/bin/twistd -n web --path /srv/hubhook
```

By default, this will bind to port 8080.
If you need to put it on another port, the `--port` parameter is your friend.
You will need to configure your firewall to allow inbound http requests to this port
from either your github enterprise server's IP or the github.com IPs
(these are 204.232.175.64/27 192.30.252.0/22 at the time of this writing but may change).

Testing
-------

Create a junk commit and push it to your repo.
Check to confirm that it propagates.
Then edit history and `git push --force` to get rid of the junk commit.
Check to confirm that it propagates.

Automated Installation
----------------------

The cool kids might want to check out http://github.com/AnchorFree/salt-formula