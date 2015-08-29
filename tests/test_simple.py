from os.path import join
import tempfile
from aioflock import LockFilename, LockFilenameTimeout
import pytest


@pytest.mark.asyncio
def test_simple_lock():
    with tempfile.TemporaryDirectory() as tmp_dir:
        lock_filename = join(tmp_dir, 'test')
        lock = LockFilename(lock_filename)
        yield from lock.acquire()
        lock2 = LockFilename(lock_filename)
        with pytest.raises(LockFilenameTimeout):
            yield from lock2.acquire(timeout=1)
        lock.release()
        yield from lock2.acquire()

@pytest.mark.asyncio
def test_with():
    with tempfile.TemporaryDirectory() as tmp_dir:
        lock_filename = join(tmp_dir, 'test')
        with (yield from LockFilename(lock_filename)):
            with pytest.raises(LockFilenameTimeout):
                with (yield from LockFilename(lock_filename, timeout=1)):
                    pass

        with (yield from LockFilename(lock_filename)):
            pass

@pytest.mark.asyncio
def test_with_exception():
    with tempfile.TemporaryDirectory() as tmp_dir:
        lock_filename = join(tmp_dir, 'test')
        with pytest.raises(Exception):
            with (yield from LockFilename(lock_filename)):
                raise Exception()

        with (yield from LockFilename(lock_filename)):
            pass