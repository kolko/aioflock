from aioflock import LockFilename, LockFilenameTimeout
import pytest


@pytest.mark.asyncio
def test_simple_lock():
    lock = LockFilename('/tmp/test_lock')
    yield from lock.acquire()
    lock2 = LockFilename('/tmp/test_lock')
    with pytest.raises(LockFilenameTimeout):
        yield from lock2.acquire(timeout=1)
    lock.release()
    yield from lock2.acquire()

@pytest.mark.asyncio
def test_with():
    with (yield from LockFilename('/tmp/test_lock')):
        with pytest.raises(LockFilenameTimeout):
            with (yield from LockFilename('/tmp/test_lock', timeout=1)):
                pass

    with (yield from LockFilename('/tmp/test_lock')):
        pass

@pytest.mark.asyncio
def test_with_exception():
    with pytest.raises(Exception):
        with (yield from LockFilename('/tmp/test_lock')):
            raise Exception()

    with (yield from LockFilename('/tmp/test_lock')):
        pass