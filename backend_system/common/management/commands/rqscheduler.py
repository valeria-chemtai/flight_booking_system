"""
Custom rqscheduler command based on how django_rq runs rqscheduler jobs
https://github.com/rq/django-rq/blob/master/django_rq/management/commands/rqscheduler.py
"""
from importlib import import_module
import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from django_rq import get_scheduler


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__
    args = '<queue>'

    def add_arguments(self, parser):
        parser.add_argument('--pid', action='store', dest='pid',
                            default=None, help='PID file to write the scheduler`s pid into')
        parser.add_argument('--interval', '-i', type=int, dest='interval',
                            default=60, help="""How often the scheduler checks for new jobs to add to the
                            queue (in seconds).""")
        parser.add_argument('--queue', dest='queue', default='default',
                            help="Name of the queue used for scheduling.",)
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        pid = options.get('pid')
        if pid:
            with open(os.path.expanduser(pid), "w") as fp:
                fp.write(str(os.getpid()))

        scheduler = get_scheduler(name=options.get('queue'), interval=options.get('interval'))
        cron_jobs = getattr(settings, 'RQ_CRON_JOBS')

        scheduled_job_ids = []

        for cron_job in cron_jobs:
            func = cron_job['func']
            if isinstance(func, str):
                module, sep, attribute = func.rpartition('.')
                mod = import_module(module)
                cron_job['func'] = getattr(mod, attribute)

            job_id = f'{cron_job['func'].__module__}.{cron_job['func'].__name__}'
            scheduled_job_ids.append(job_id)

            if job_id in scheduler:
                # dequeue job if it had been initially queued
                job = scheduler.job_class.fetch(job_id, connection=scheduler.connection)
                scheduler.cancel(job)

            logger.info(f'Scheduling job {job_id} with schedule {cron_job["cron_string"]}')
            scheduler.cron(
                cron_string=cron_job.get('cron_string'),
                func=cron_job.get('func'),
                args=cron_job.get('args'),
                kwargs=cron_job.get('kwargs'),
                repeat=cron_job.get('repeat'),
                queue_name=cron_job.get('queue_name', 'default'),
                id=job_id,
            )
        # cancel all jobs that are not in the settings file currently
        bad_cron_jobs = [
            job for job in scheduler.get_jobs()
            if job.id not in scheduled_job_ids
        ]
        for job in bad_cron_jobs:
            scheduler.cancel(job)

        scheduler.run()
