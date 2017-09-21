from unittest import TestCase

from multiprocessing import Queue
import shutil
import tempfile
import time


from watchdog.observers import Observer

from ojo.models.watcher import NewJobsWatcher
from ojo.models.job import JobFactory, JobStage


class TestWatcherJobFactory(TestCase):
    def setUp(self):
        self.job_factory = JobFactory(working_dir="working_dir", done_dir="done_dir")
        self.queue = Queue(maxsize=10)
        self.watcher = NewJobsWatcher(self.job_factory, self.queue)
        self.observer = Observer()
        self.path = tempfile.mkdtemp()
        self.observer.schedule(self.watcher, self.path, recursive=False)
        self.observer.start()

    def tearDown(self):
        self.observer.stop()
        self.observer.join(timeout=0.1)
        shutil.rmtree(self.path)

    def create_file(self, file_name, content, path=None):
        f = tempfile.NamedTemporaryFile(
            prefix=file_name,
            dir=path or self.path,
            delete=False,
        )
        f.write(content)
        f.close()
        time.sleep(1)

    def get_jobs(self):
        self.queue.put("poison pill")
        results = []
        a = self.queue.get()
        while "poison pill" != a:
            results.append(a)
            a = self.queue.get()
        return results

    def test_1_job_from_1_file(self):
        self.create_file("111", "111111111")
        jobs = self.get_jobs()
        self.assertEqual(1, len(jobs))
        job = jobs[0]
        self.assertEqual(
            job.stage, JobStage.created
        )

    def test_3_job_from_3_files(self):
        self.create_file("111", "111111111")
        self.create_file("222", "111111111")
        self.create_file("333", "111111111")
        jobs = self.get_jobs()
        self.assertEqual(3, len(jobs))

    def test_dir_with_mult_files_is_one_job(self):
        path = tempfile.mkdtemp()
        self.create_file("111", "111111111", path)
        self.create_file("222", "111111111", path)
        self.create_file("333", "111111111", path)
        shutil.move(path, self.path)
        time.sleep(1)
        jobs = self.get_jobs()
        self.assertEqual(1, len(jobs))
