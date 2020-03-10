cd /home/ubuntuadmin/staging/UAC
git stash
git pull origin master

source /home/ubuntuadmin/staging/venv/bin/activate

pip install -r  requirments.txt

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic <<<yes

sudo pkill -9 -f uwsgi
nohup uwsgi --ini /etc/uwsgi/sites/uac_staging.ini >/dev/null 2>&1 &
sudo service nginx restart

deactivate 
cd -

