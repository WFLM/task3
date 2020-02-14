from threading import Thread, Lock
from itertools import count
from abc import ABCMeta, abstractmethod


class ThreadSafeCounter(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, value=0, step=1):
        pass

    @abstractmethod
    def increment(self):
        pass

    @property
    @abstractmethod
    def value(self):
        pass


class SharedCounter(ThreadSafeCounter):
    def __init__(self, value=0, step=1):
        self._value = value
        self._step = step
        self._lock = Lock()

    def increment(self):
        with self._lock:  # The next thread is locked here while the previous thread is making all 3 steps:
            self._value += self._step  # read-process-write

    @property
    def value(self):
        return self._value


class FastSharedCounter(ThreadSafeCounter):
    def __init__(self, value=0, step=1):
        self._step = step
        self._read_number = 0
        self._counter = count(value, step)
        self._lock = Lock()

    def increment(self):
        next(self._counter)  # Lock here not needed because it's an atomic operation

    @property
    def value(self):  # But this complex read-process-write operation is not
        with self._lock:
            value = next(self._counter) - self._read_number
            self._read_number += self._step
        return value


# counter = SharedCounter()
counter = FastSharedCounter()


def function(arg):
    for _ in range(arg):
        # a += 1  <- The main problem here that this operation is done in 3 steps: read-process-write.
        #            If a usual integer value, any other process may invade these steps.
        #            In this case, we should use a counter.
        #            But if we want to have all operators ("+=, -=, *=, etc.), we can make something like AtomicInteger.
        #            But it's unusable in this case (lots of operations) because it will work very slow.
        counter.increment()


def main():
    threads = []
    for i in range(5):
        thread = Thread(target=function, args=(1000000,))
        thread.start()
        threads.append(thread)

    [t.join() for t in threads]
    print("----------------------", counter.value)  # ???


main()
