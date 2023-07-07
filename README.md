# Iceberg in AWS Lambda
Demo using PyIceberg in AWS Lambda

## Issue

## Problem

PyIceberg currently relies on [`multiprocessing`](https://docs.python.org/3/library/multiprocessing.html) in [`Table.plan_files`](https://github.com/apache/iceberg/blob/a73f10b3e7a98d7efcab7e01382b78bffdc7028e/python/pyiceberg/table/__init__.py#L776). Unfortunately, this module relies on `/dev/shm`, which is not provided by serverless runtimes like [Lambda](https://aws.amazon.com/blogs/compute/parallel-processing-in-python-with-aws-lambda/) and [Fargate](https://github.com/aws/containers-roadmap/issues/710). In effect, this assumes the user has control over the host environment and thus does not work in serverless environments.

[Apparently](https://github.com/lambci/docker-lambda/issues/75#issuecomment-668897239), One way to emulate Lambda or Fargate behavior locally is to run a Docker image with [`--ipc="none"`](https://docs.docker.com/engine/reference/run/#ipc-settings---ipc). This will disable the `/dev/shm` mount and cause the `multiprocessing` module to fail with the following error:

```python
[ERROR] OSError: [Errno 38] Function not implemented
Traceback (most recent call last):
  File "/var/task/app.py", line 27, in handler
    result = scan.to_arrow().slice_length(limit)
  File "/var/task/pyiceberg/table/__init__.py", line 819, in to_arrow
    self.plan_files(),
  File "/var/task/pyiceberg/table/__init__.py", line 776, in plan_files
    with ThreadPool() as pool:
  File "/var/lang/lib/python3.10/multiprocessing/pool.py", line 930, in __init__
    Pool.__init__(self, processes, initializer, initargs)
  File "/var/lang/lib/python3.10/multiprocessing/pool.py", line 196, in __init__
    self._change_notifier = self._ctx.SimpleQueue()
  File "/var/lang/lib/python3.10/multiprocessing/context.py", line 113, in SimpleQueue
    return SimpleQueue(ctx=self.get_context())
  File "/var/lang/lib/python3.10/multiprocessing/queues.py", line 341, in __init__
    self._rlock = ctx.Lock()
  File "/var/lang/lib/python3.10/multiprocessing/context.py", line 68, in Lock
    return Lock(ctx=self.get_context())
  File "/var/lang/lib/python3.10/multiprocessing/synchronize.py", line 162, in __init__
    SemLock.__init__(self, SEMAPHORE, 1, 1, ctx=ctx)
  File "/var/lang/lib/python3.10/multiprocessing/synchronize.py", line 57, in __init__
    sl = self._semlock = _multiprocessing.SemLock(
```

## Proposal

I think PyIceberg should support multiple concurrency strategies, allowing the user to configure which one suits their runtime/resources best.

Instead of using the multiprocessing module directly, we could instead depend on a concrete ipmlementation of an [`Executor`](https://docs.python.org/3/library/concurrent.futures.html#executor-objects) from the [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html) module. The user can select the appropriate implementation depending on a configuration value:

- `PYICEBERG__CONCURRENCY=multiprocessing` uses the [`ProcessPoolExecutor`](https://docs.python.org/3/library/concurrent.futures.html#processpoolexecutor) (default, same as current implementation)
- `PYICEBERG__CONCURRENCY=threading` uses the [`ThreadPoolExecutor`](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor) (appropriate for serverless environments)

This would allow us to support other concurrency models in the future, even supporting user-defined implementations of the `Executor` ABC.

I'd be happy to work on this feature once the community agrees on a direction.