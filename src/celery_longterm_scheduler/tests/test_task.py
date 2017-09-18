from datetime import datetime
import celery
import celery_longterm_scheduler
import mock


TESTAPP = celery.Celery(task_cls=celery_longterm_scheduler.Task)


@TESTAPP.task
def echo(arg):
    return arg


def test_should_store_all_arguments_needed_for_send_task():
    # Cannot do this with a Mock, since they (technically correctly)
    # differentiate recording calls between args and kw, so a call
    # `send_task(1, 2,  3)` is not considered equal to
    # `send_task(1, args=2, kwargs=3)`, although semantically it is the same.
    def record_task(
            name, args=None, kwargs=None, countdown=None, eta=None,
            task_id=None, producer=None, connection=None, router=None,
            result_cls=None, expires=None, publisher=None, link=None,
            link_error=None, add_to_parent=True, group_id=None, retries=0,
            chord=None, reply_to=None, time_limit=None, soft_time_limit=None,
            root_id=None, parent_id=None, route_name=None, shadow=None,
            chain=None, task_type=None, **options):
        options.update(dict(
            args=args, kwargs=kwargs, countdown=countdown,
            eta=eta, task_id=task_id, producer=producer, connection=connection,
            publisher=publisher, link=link, link_error=link_error,
            add_to_parent=add_to_parent, group_id=group_id, retries=retries,
            chord=chord, reply_to=reply_to, time_limit=time_limit,
            soft_time_limit=soft_time_limit, root_id=root_id,
            parent_id=parent_id, route_name=route_name, shadow=shadow,
            chain=chain, task_type=task_type
        ))
        calls.append((name, options))
    calls = []

    with mock.patch.object(TESTAPP, 'send_task', new=record_task):
        with mock.patch(
                'celery_longterm_scheduler.get_scheduler') as scheduler:
            echo.apply_async(('foo',), eta=datetime.now())
            scheduler = scheduler()
            args = scheduler.store.call_args[0][2]
            kw = scheduler.store.call_args[0][3]
            # schedule() always generates an ID itself (to reuse it for the
            # scheduler storage), while the normal apply_async() defers that to
            # send_task(). We undo this here for comparison purposes.
            kw['task_id'] = None
            TESTAPP.send_task(*args, **kw)
            scheduled_call = calls[0]

            echo.apply_async(('foo',))
            normal_call = calls[1]
            assert scheduled_call == normal_call