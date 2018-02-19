from multiprocessing import JoinableQueue, Process

from ojo.workers import rar

from ojo.config import config

if __name__ == "__main__":
    print("START")
    if not rar.is_installed():
        print("RAR is not installed on system! ")
        exit(-1)

    work_q = JoinableQueue()
    done_q = JoinableQueue()
    error_q = JoinableQueue()

    this_config = config.load()
    ps = [
        Process(
            name="p-%d" % i,
            target=rar.rar_worker,
            args=(this_config, "w-%d" % i, work_q, done_q, error_q))
        for i in range(3)
    ]
    for p in ps:
        p.daemon = True
        p.start()
    for i in range(10):
        work_q.put("job-%d" % i)

    for p in ps:
        work_q.put(None)

    for i in range(10):
        print(done_q.get())
        done_q.task_done()

    print("done q join")
    done_q.join()
    print("work q join")
    work_q.join()
    print("error q join")
    error_q.join()

    for p in ps:
        print("process join")
        p.join(1)
        print("joined")
