import logging
import time

from watchdog.events import FileSystemEventHandler


class WatchService(FileSystemEventHandler):
    """
        First of the services, so behaves differently. Maybe it should not live here
    """

    def __init__(self, job_maker, job_queue):
        self.job_maker = job_maker
        self.job_queue = job_queue

    def on_created(self, event):
        new_job = self.job_maker(event.src_path)
        logging.info("Pushing new job : %s" % new_job)
        time.sleep(1)
        self.job_queue.put(new_job)
