# Implements a diana-star Celery worker

from celery import Celery


app = Celery('diana',
             include = ['diana.distrib.tasks',
                        'diana.daemon.tasks'])

app.conf.update(
    result_expires = 3600,
    task_serializer = "pickle",
    accept_content = ["pickle"],
    result_serializer = "pickle",
    task_default_queue = 'default',
    task_routes={'*.classify': {'queue': 'learn'},    # Only GPU boxes
                 '*.file':     {'queue': 'file'} },   # Access to shared fs
)

app.config_from_object('celerycfg')

if __name__ == '__main__':
    app.start()
