import celery
import celery.contrib.testing.app
import celery_longterm_scheduler
import pytest


CELERY = celery.Celery(task_cls=celery_longterm_scheduler.Task)


@pytest.fixture(scope='session')
def celery_app(request):
    CELERY.conf.update(celery.contrib.testing.app.DEFAULT_TEST_CONFIG)
    worker = celery.contrib.testing.worker.start_worker(CELERY)
    worker.__enter__()
    request.addfinalizer(lambda: worker.__exit__(None, None, None))


# celery.contrib.testing.worker expects a 'ping' task, so it can check that the
# worker is running properly.
@CELERY.task(name='celery.ping')
def celery_ping():
    return 'pong'