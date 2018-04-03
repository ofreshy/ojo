import logging

from ojo.services.error_service import ErrorService
from ojo.services.move_service import MoveService
from ojo.services.par2_service import Par2Service
from ojo.services.rar_service import RarService

from multiprocessing import JoinableQueue, Process
from ojo.config import config
from ojo import observer
from ojo.worker import make_error_worker, make_worker


class Builder(object):
    def __init__(self, conf=None):
        self.conf = conf or config.load()

        self.to_move_q = JoinableQueue()
        self.to_rar_q = JoinableQueue()
        self.to_par_q = JoinableQueue()
        self.to_upload_q = JoinableQueue()
        self.error_q = JoinableQueue()

        self.observer = observer.build_observer(self.conf, self.to_move_q)
        self.error_service = ErrorService.make(self.conf)

        self._processes = []

    def _build_error_processes(self):
        self._processes.append(
            Process(
                name="error_process-1",
                target=make_error_worker(
                    "error-worker-1",
                    self.error_service,
                    self.error_q,
                )
            )
        )

    def _build_move_processes(self):
        self._create_processes(
            "move",
            MoveService.make(self.conf),
            self.to_move_q,
            self.to_rar_q,
            1,
        )

    def _build_rar_processes(self):
        self._create_processes(
            "rar",
            RarService.make(self.conf),
            self.to_rar_q,
            self.to_par_q,
            int(self.conf["rar_service"]["num_workers"]),
        )

    def _build_par2_processes(self):
        self._create_processes(
            "par2",
            Par2Service.make(self.conf),
            self.to_par_q,
            self.to_upload_q,
            int(self.conf["par2_service"]["num_workers"]),
        )

    def _create_processes(self, base_name, service, work_q, done_q, num):
        processes = [
            Process(
                name="{0}_process-{1}".format(base_name, i),
                target=make_worker(
                    name="{0}-worker-{1}".format(base_name, i),
                    service=service,
                    work_q=work_q,
                    done_q=done_q,
                    error_q=self.error_q,
                )
            )
            for i in range(num)
        ]
        self._processes += processes
        return processes

    def build(self):
        self._build_error_processes()
        self._build_move_processes()
        self._build_rar_processes()
        self._build_par2_processes()
        return self

    def start(self):
        try:
            for p in reversed(self._processes):
                p.daemon = True
                p.start()

            self.observer.start()
            self.observer.join()
        except AttributeError as ae:
            logging.fatal("must call build before calling start", ae)
            exit(64)
