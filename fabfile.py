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
    local('find . \( -name "*.pyc" -or -name "*.pyo" -or -name "*py.class" \) -delete')

    local('tar cf %(stamptar)s run.sh' % env)
    local('tar rf %(stamptar)s requirements.deploy' % env)
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
                sudo('virtualenv venv -p $(pyenv prefix 3.5.1)/bin/python' % env)

            with path('./venv/bin', behavior='prepend'):
                sudo('pip install --quiet --no-cache-dir -r ./src/requirements.deploy' % env)

        with cd('/home/%(server_user)s/run' % env):
            sudo('ln -nsf $(basename $(readlink -f current)) previous' % env)
            sudo('ln -nsf %(stamp)s current' % env)


@task
def clean():
    with settings(sudo_user=server_user):
        with cd('/home/%(server_user)s/run' % env):
            sudo('current=$(basename $(readlink -f current)) && previous=$(basename $(readlink -f previous)) && for dir in $(ls -dt */ | egrep -v "current|previous|$current|$previous"); do rm -r $dir; done')
