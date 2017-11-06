
def worker(queue, done_q):
    while True:
        msg = queue.get()  # Read from the queue and do nothing
        if (msg == 'DONE'):
            done_q.put(msg)

            break



    return


def work_on(job):
    print("got job %s" % job)


if __name__ == "__main__":
    from multiprocessing import Process, Queue
    produce_on = Queue()
    consume_from = Queue()

    ps = [Process(name="p-%d"%i, target=worker, args=(consume_from, produce_on)) for i in range(3)]
    for p in ps:
        p.daemon = True
        p.start()
    for i in range(10):
        consume_from.put("job-%d" % i)
    consume_from.put("DONE")

    for p in ps:
        consume_from.put("DONE")

    for p in ps:
        p.join()
    print(produce_on.get(), produce_on.get(), produce_on.get())


