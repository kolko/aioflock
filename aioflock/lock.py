import fcntl
import time
from functools import partial

from asyncio import coroutine, get_event_loop, sleep
# from asyncio import compat

from .exceptions import LockFilenameTimeout


class _ContextManager:
    """Context manager.
    This enables the following idiom for acquiring and releasing a
    lock around a block:
        with (yield from lock):
            <block>
    while failing loudly when accidentally using:
        with lock:
            <block>
    """

    def __init__(self, lock):
        self._lock = lock

    def __enter__(self):
        # We have no use for the "as ..."  clause in the with
        # statement for locks.
        return None

    def __exit__(self, *args):
        try:
            self._lock.release()
        finally:
            self._lock = None  # Crudely prevent reuse.


class _ContextManagerMixin:
    def __enter__(self):
        raise RuntimeError(
            '"yield from" should be used as context manager expression')

    def __exit__(self, *args):
        # This must exist because __enter__ exists, even though that
        # always raises; that's how the with-statement works.
        pass

    @coroutine
    def __iter__(self):
        # This is not a coroutine.  It is meant to enable the idiom:
        #
        #     with (yield from lock):
        #         <block>
        #
        # as an alternative to:
        #
        #     yield from lock.acquire()
        #     try:
        #         <block>
        #     finally:
        #         lock.release()
        yield from self.acquire()
        return _ContextManager(self)

    # if compat.PY35:
    #
    #     def __await__(self):
    #         # To make "with await lock" work.
    #         yield from self.acquire()
    #         return _ContextManager(self)
    #
    #     @coroutine
    #     def __aenter__(self):
    #         yield from self.acquire()
    #         # We have no use for the "as ..."  clause in the with
    #         # statement for locks.
    #         return None
    #
    #     @coroutine
    #     def __aexit__(self, exc_type, exc, tb):
    #         self.release()


class LockFilename(_ContextManagerMixin):
    def __init__(self, filename, timeout=None):
        self.f = open(filename, 'w+')
        self.timeout = timeout

    @coroutine
    def acquire(self, timeout=None, loop=None, executor=None):
        try:
            # First try fast lock
            fcntl.flock(self.f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            if loop is None:
                loop = get_event_loop()
            in_executor = partial(self._sync_flock, timeout=timeout)
            f = yield from loop.run_in_executor(executor, in_executor)
            yield from f

    def release(self):
        fcntl.flock(self.f.fileno(), fcntl.LOCK_UN)

    @coroutine
    def _sync_flock(self, timeout=None):
        st_time = time.time()
        while True:
            try:
                fcntl.flock(self.f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                if timeout or self.timeout:
                    if time.time() - st_time > (timeout or self.timeout):
                        raise LockFilenameTimeout()
                yield from sleep(1)