# SpotipyWeb

How to run:
1. Go to SpotipyWeb folder
2. $ virtualenv venv
3. $ source /venv/bin/activate
4. $ pip install flask
5. $ pip install flask-wtf
6. $ pip install flask-sqlalchemy
7. $ flask db init
8. $ flask db migrate -m "import tables"
9. $ flask db upgrade
10. $ pip install flask-login
11. $ export FLASK_APP=main.py
12. $ flask run

Then go to localhost
