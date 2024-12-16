
first create virtual env
```
python3 -m venv myenv
```
Activate the Virtual Environment
```
source myenv/bin/activate
```

run below cmd
```
pip install -r requirements.txt
```

test case
```
python manage.py test video_app
```
## if we are using same sqlite file 

run server
```
python manage.py runserver 
```


## if we are not using same sqlite file 

```
python manage.py migrate
python manage.py createsuperuser --username admin --email admin@example.com
```
set apassword
```
```
run server
```
python manage.py runserver 
```

login to below link to generate token via django Administration to use Postman
```
http://127.0.0.1:8000/admin/login/?next=/admin/
```
