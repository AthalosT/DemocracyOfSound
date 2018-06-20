# SpotipyWeb

How to run:
1. Go to SpotipyWeb folder
2. $ virtualenv venv
3. $ source /venv/bin/activate
4. $ pip install flask
5. $ pip install flask-wtf
6. $ pip install flask-sqlalchemy
7. $ pip install flask-migrate
8. $ pip install flask-login
9. $ export FLASK_APP=main.py 
10. $ flask db init
11. $ flask db migrate -m "import tables"
12. $ flask db upgrade
13. $ flask run

Then go to localhost
