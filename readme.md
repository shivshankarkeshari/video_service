
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

## if we are using same sqlite file 

run server
```
python manage.py runserver 
```

test
```
```

## if we are not using same sqlite file 

```
python manage.py migrate
python manage.py createsuperuser --username admin --email admin@example.com
```
set apassword

login to below link to generate token via django Administration
```
http://127.0.0.1:8000/admin/login/?next=/admin/
```
