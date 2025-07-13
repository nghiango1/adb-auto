"""Check for info: https://docs.gunicorn.org/en/stable/settings.html"""

from adb_auto.main import start_background_jobs, exit_background_jobs


def on_starting(server):
    start_background_jobs()


def on_exit(server):
    exit_background_jobs()


def pre_fork(server, worker):
    pass


def post_fork(server, worker):
    pass
