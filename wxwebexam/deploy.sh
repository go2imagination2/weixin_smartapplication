ps aux|grep gunicorn |awk '{print $2}'|xargs kill -9
cp db.sqlite3 db.sqlite3~
git pull
#python manage.py loadata fixture.json
gunicorn --workers=2 -k gevent wxwebexam.wsgi:application &
