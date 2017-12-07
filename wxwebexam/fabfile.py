from fabric.api import local, run, warn_only
from fabric.context_managers import cd, lcd, shell_env, settings
from fabric.utils import abort, puts
from fabric import colors
from datetime import datetime

HOST = '47.93.224.23'
INSTALL_FOLDER = '/root/onlineexam/wxwebexam'
DB_BACKUP_FOLDER = '/data/db-backup'


def ver():
    """fab ver
    """
    local('fab --version')
    local('python --version')
    local('python manage.py version')
    print 'Usage: fab -u root -H %s deploy' % HOST


def deploy():
    """
    fab deploy -u root -H 
    """
    with shell_env(SERVER_SOFTWARE='1'):
        with cd(INSTALL_FOLDER):
            run('echo $SERVER_SOFTWARE')
            run('git pull')
            # run('chown www-data .')
            # run('chown www-data ./sqlite3_db')
            # run('chmod u+w+x,g+w+x ./sqlite3_db')
            run('python manage.py makemigrations sports')
            run('python manage.py migrate --fake-initial')
            run('rm -rf prod-static/')
            run('python manage.py collectstatic --noinput')
            run('git rev-parse HEAD > prod-static/version.txt')
            # run('python manage.py loaddata fixtures/jiuxuan.json')


def restart():
    """
    fab restart -u root -H
    """
    with cd(INSTALL_FOLDER):
        run('pwd')
        with settings(warn_only=True):
            run('pkill python')
        run(
            'nohup python /usr/local/bin/gunicorn --workers=2 -k gevent sportsite.wsgi:application --settings sportsite.pg_settings ')
    puts(colors.green("Gunicorn restarted."))


def backupdb():
    with lcd(INSTALL_FOLDER):
        today = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')
        local('python manage.py dumpdata sports > %s%s.json' % (DB_BACKUP_FOLDER, today))
        local('zip %s%s.zip %s%s.json' % (DB_BACKUP_FOLDER, today, DB_BACKUP_FOLDER, today))
        local('rm %s%s.json' % (DB_BACKUP_FOLDER, today))


def restoredb():
    with lcd(INSTALL_FOLDER):
        local('python manage.py loaddata fixtures/jiuxuan.json')
