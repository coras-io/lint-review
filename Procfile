web: gunicorn -c settings.py lintreview.web:app --log-file -
worker: celery -A lintreview.tasks worker
