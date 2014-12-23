import datetime
import git
import json
import os
import os.path
from subprocess import call
from twisted.web.resource import Resource
from twisted.python import log
from urlparse import urlparse


# All repos are presumed to be checked out under /src/{reponame}
# For interactions with origin, use ~/.ssh/{repname}_deploy_key

class Hook(Resource):
    isLeaf = True

    def render_POST(self, request):
        """
        Support both the old application/vnd.github.v3+form format and the new application/vnd.github.v3+json format
        for webhooks.
        """
        p = json.loads(request.args['payload'][0]) if request.args else json.load(request.content)
        u = urlparse(p['repository']['url'])
        owner, repo_name = os.path.split(u.path)

        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]

        repo_path = os.path.join('/srv', repo_name)
        repo = git.Repo(repo_path)
        repo.remotes.origin.fetch(prune=True)
        repo.head.reset(commit='origin/master', index=True, working_tree=True)

        # I don't know how to do this using GitPython yet.
        os.chdir(repo_path)
        call(['git', 'submodule', 'update', '--init'])

        obj = repo.head.object

        dt = datetime.datetime.fromtimestamp(obj.committed_date)
        log.msg('{0!r} now at commit {1} from {2}'.format(repo_path, obj.hexsha, dt.isoformat()))

        return ''

resource = Hook()
