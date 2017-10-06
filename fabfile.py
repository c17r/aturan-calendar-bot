from datetime import datetime
from fabric.api import task, env, settings, cd, sudo, run, local, put, path, shell_env

server_user = 'aturan_calendar'

stamp = datetime.now().strftime("v%Y%m%d%H%M%S")
stamptar = server_user + "-" + stamp + ".tar"
stampzip = stamptar + ".gz"

env.stamp = stamp
env.stamptar = stamptar
env.stampzip = stampzip
env.server_user = server_user

@task
def live():
    env.hosts = [
        "crow.endrun.org"
    ]

@task
def deploy():
    local('make clean')
    local('pipenv run python setup.py sdist bdist_wheel --universal')

    local('tar cf %(stamptar)s run.sh' % env)
    local('(cd dist && tar rf ../%(stamptar)s *.tar.gz)' % env)
    local('gzip %(stamptar)s' % env)

    put(stampzip, '/tmp/%(stampzip)s' % env)

    local('rm %(stampzip)s' % env)

    with settings(sudo_user=server_user):

        with cd('/home/%(server_user)s/run' % env):
            sudo('mkdir -p %(stamp)s/src' % env)
            sudo('mkdir -p %(stamp)s/venv' % env)

        with cd('/home/%(server_user)s/run/%(stamp)s' % env):
            sudo('tar xfz /tmp/%(stampzip)s -C ./src/' % env)

    sudo('rm /tmp/%(stampzip)s' % env)

    with settings(sudo_user=server_user):

        with cd('/home/%(server_user)s/run/%(stamp)s' % env):
            with shell_env(PATH='/opt/pyenv/bin/:$PATH', PYENV_ROOT='/opt/pyenv'):
                sudo('virtualenv venv -p $(pyenv prefix 3.6.2)/bin/python' % env)

            with path('./venv/bin', behavior='prepend'):
                sudo('pip install --quiet --no-cache-dir ./src/*.tar.gz' % env)

        with cd('/home/%(server_user)s/run' % env):
            sudo('ln -nsf $(basename $(readlink -f current)) previous' % env)
            sudo('ln -nsf %(stamp)s current' % env)


@task
def prune():
    with settings(sudo_user=server_user):
        with cd('/home/%(server_user)s/run' % env):
            sudo('[ -h current ] && $(for dir in $(ls -1f | grep -e "/$" | grep -ve "$(readlink previous)\|$(readlink current)"); do rm -r $dir; done) || true')
