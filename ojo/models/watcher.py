import logging

from watchdog.events import FileSystemEventHandler


class NewJobsWatcher(FileSystemEventHandler):

    def __init__(self, job_factory, job_queue):
        self.job_factory = job_factory
        self.job_queue = job_queue

    def on_created(self, event):
        new_job = self.job_factory.make(event.src_path)
        logging.info("Pushing new job : %s" % new_job)
        self.job_queue.put(new_job)
