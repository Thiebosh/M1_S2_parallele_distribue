import asyncio
import sys
import contextlib


async def ainput(event_end):
    await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
    event_end.set()


async def event_wait(evt, timeout):
    # suppress TimeoutError because we'll return False in case of timeout
    with contextlib.suppress(asyncio.TimeoutError):
        await asyncio.wait_for(evt.wait(), timeout)
    return evt.is_set()

async def thread_pool_async(event_end, nb_threads, work_queue):
    # for _ in range nb_threads;
    # event et work_queue commun
    pass
