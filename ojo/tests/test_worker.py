from unittest import TestCase

from multiprocessing import Process, Queue
import tempfile
import time

from ojo import worker



class TestWatcherJobFactory(TestCase):
    def setUp(self):
        self.job_id = 0
        self.queue = Queue(maxsize=10000)


    def tearDown(self):
        pass


    def create_file(self, file_name, content, path=None):
        f = tempfile.NamedTemporaryFile(
            prefix=file_name,
            dir=path or self.path,
            delete=False,
        )
        f.write(bytes(content, encoding="utf-8"))
        f.close()
        time.sleep(1)

    def add_job(self):
        self.job_id += 1
        job = "job-%s" % self.job_id
        self.queue.put(job)
        return job

    def terminate(self):
        self.queue.put("DONE")

    def test_worker_accepts_jobs(self):
        q = Queue()
        p = Process(target=worker.worker, name="process-1", args=(self.queue, q))
        p.start()

        for _ in range(5000):
            self.add_job()

        self.terminate()
        p.join()

        i = 0
        while q.get() != "DONE":
            i+=1
        print(i)





