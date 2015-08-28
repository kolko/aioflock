aioflock: file lock support for asyncio (based on fcntl.flock)
==================================


.. image:: https://img.shields.io/pypi/v/aioflock.svg
    :target: https://pypi.python.org/pypi/aioflock

.. image:: https://coveralls.io/repos/kolko/aioflock/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/kolko/aioflock?branch=master

.. image:: https://travis-ci.org/kolko/aioflock.svg?branch=master
    :target: https://travis-ci.org/kolko/aioflock



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