web: sh -c 'cd ./backend_system/ && exec gunicorn config.wsgi --log-file -'
worker: python backend_system/manage.py rqworker default
scheduler: python backend_system/manage.py rqscheduler