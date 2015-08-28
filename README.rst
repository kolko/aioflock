aioflock: file lock support for asyncio (based on fcntl.flock)
==================================


Example:

.. code-block:: python

    from aioflock import LockFilename
    lock = LockFilename('/tmp/test_lock')
    yield from lock.acquire()
    ..inside lock..
    lock.release()



With stategment:

.. code-block:: python

    from aioflock import LockFilename
    with (yield from LockFilename('/tmp/test_lock')):
        ..inside lock..



Can use timeout:

.. code-block:: python

    from aioflock import LockFilename, LockFilenameTimeout

    try:
        with (yield from LockFilename('/tmp/test_lock')):
            with (yield from LockFilename('/tmp/test_lock', timeout=1)):
                ...newer here...
    except LockFilenameTimeout:
        ...here...