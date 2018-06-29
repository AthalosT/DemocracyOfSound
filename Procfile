web: gunicorn -k eventlet --worker-class socketio.sgunicorn.GeventSocketIOWorker project:app
init: python3 manage.py db init
migrate: python3 manage.py db migrate
upgrade: python3 manage.py db upgrade
