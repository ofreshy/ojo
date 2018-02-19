import logging
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from ojo.models.job import Job


class WatchService(FileSystemEventHandler):
    """
        First of the services, so behaves differently. Maybe it should not live here
    """
    def __init__(self, job_queue, sleep_time=1):
        self.job_queue = job_queue
        self.sleep_time = int(sleep_time)

    def on_created(self, event):
        new_job = Job.make(event.src_path)
        logging.info("Pushing new job : %s" % new_job)
        time.sleep(self.sleep_time)
        self.job_queue.put(new_job)


def build_observer(conf, work_q):
    observer = Observer()
    observer.schedule(
        WatchService(
            work_q,
            conf["observer"]["sleep_time_seconds"],
        ),
        conf["observer"]["dir"],
        recursive=False,
    )
    return observer
