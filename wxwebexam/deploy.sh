ps aux|grep gunicorn |awk '{print $2}'|xargs kill -9
python manage.py dumpdata  --format json   > /data/db-backup/`date +"%Y-%m-%d-%H-%M-%S"`.json
###cp db.sqlite3 db.sqlite3~
git pull
###python manage.py loaddata --app scrum.entry fixture.json
gunicorn --workers=2 -k gevent wxwebexam.wsgi:application &
