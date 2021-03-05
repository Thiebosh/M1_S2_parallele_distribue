import asyncio
import sys
import contextlib
import threading
from talk_to_ftp import TalkToFTP
from logger import Logger


async def ainput(evt_end):
    await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
    evt_end.set()


async def event_wait(evt, timeout):
    if evt.is_set():
        return True
    # suppress TimeoutError because we'll return False in case of timeout
    with contextlib.suppress(asyncio.TimeoutError):
        await asyncio.wait_for(evt.wait(), timeout)
    return evt.is_set()


# thread section

async def synchronous_core(lock, queue_high, queue_low, evt_done_main, evt_done_workers, frequency, duration):
    task = None

    async with lock:
        if not queue_high.empty():
            task = await queue_high.get()

        elif not queue_low.empty():
            task = await queue_low.get()

    if not task and evt_done_main.is_set():
        evt_done_main.clear()
        evt_done_workers.set()
        # store timestamp
        duration = frequency

    return task, duration

async def async_worker(id, ftp_website, main_loop, lock, queue_high, queue_low,
                       evt_end, evt_done_main, evt_done_workers, frequency):
    ftp = TalkToFTP(ftp_website)
    functions = {"create_folder": ftp.create_folder,
                 "remove_file": ftp.remove_file,
                 "file_transfer": ftp.file_transfer,
                 "remove_folder": ftp.remove_folder}

    core_args = (lock, queue_high, queue_low, evt_done_main, evt_done_workers, frequency, 1)

    try:
        duration = 0
        while not asyncio.run_coroutine_threadsafe(event_wait(evt_end, duration), main_loop).result(): # run on main thread's loop

            if evt_done_workers.is_set():
                duration = frequency # - timestamp diff
                continue

            task, duration = asyncio.run_coroutine_threadsafe(synchronous_core(*core_args), main_loop).result() # run on main thread's loop

            if not task:
                continue

            try:
                ftp.connect()

                if task[0] in functions:
                    functions[task[0]](*task[1])
                else:
                    Logger.log_critical(f"thread {id} - Unknow method")

                ftp.disconnect()
                task = None

            except Exception as e:
                Logger.log_critical(f"thread {id} - {e}")
                break

    except Exception as e:
        Logger.log_critical(f"thread {id} - {e}")

    finally:
        if evt_done_main.is_set():
            evt_done_main.clear()
            main_loop.call_soon_threadsafe(lambda: evt_done_workers.set()) # run on main thread's loop

        Logger.log_info(f"thread {id} - Stop")


def thread_pool(nb_threads, worker_args):
    for id in range(nb_threads):
        threading.Thread(target=lambda:asyncio.run(async_worker(id, *worker_args))).start()
