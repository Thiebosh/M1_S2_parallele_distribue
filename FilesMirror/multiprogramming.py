import asyncio
import sys
import contextlib
import threading
from talk_to_ftp import TalkToFTP
from logger import Logger
import time
import multiprocessing
from ftplib import error_perm


async def async_input(evt_end):
    await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
    Logger.log_info(f"Get stop signal, wait end of running tasks")
    evt_end.set()


async def event_wait(evt, timeout):
    if evt.is_set():
        return True

    try:
        # suppress TimeoutError because we'll return False in case of timeout
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(evt.wait(), timeout)

    except Exception: # future are broken by keyboard interrupt
        evt.set() # keyboard interrupt

    return evt.is_set()


# thread section

async def synchronous_core(id, lock, queue, evt_done_main, evt_done_workers, frequency, duration, shared_time_ref):
    task = None

    async with lock:
        if not queue.empty():
            task = await queue.get()

    if not task and evt_done_main.is_set():
        shared_time_ref.value = time.time()
        evt_done_main.clear()
        evt_done_workers.set()
        duration = frequency

    return task, duration


async def synchronous_enqueue(lock, queue, task):
    async with lock:
        await queue.put(task)


async def async_worker(id, ftp_website, main_loop, lock, queue,
                       evt_end, shared_threads_working,
                       evt_done_main, evt_done_workers, frequency, shared_time_ref):
    ftp = TalkToFTP(ftp_website)
    functions = {"create_folder": ftp.create_folder,
                 "remove_file": ftp.remove_file,
                 "file_transfer": ftp.file_transfer,
                 "remove_folder": ftp.remove_folder}

    core_args = (id, lock, queue, evt_done_main, evt_done_workers, frequency, 1, shared_time_ref)

    try:
        duration = 0
        while not asyncio.run_coroutine_threadsafe(event_wait(evt_end, duration), main_loop).result(): # run on main thread's loop

            if evt_done_workers.is_set():
                duration = frequency - ((time.time() - shared_time_ref.value) % frequency)
                continue

            task, duration = asyncio.run_coroutine_threadsafe(synchronous_core(*core_args), main_loop).result() # run on main thread's loop

            if not task:
                continue

            ftp.connect()

            if task[0] in functions:
                try:
                    functions[task[0]](*task[1])
                except error_perm: # "425 Can't open data connection for transfer of '...'"
                    if task[0] != "create_folder" and error_perm[:3] != "550": # "550 Directory already exists"
                        asyncio.run_coroutine_threadsafe(synchronous_enqueue(lock, queue, task), main_loop) # retry later

            else:
                Logger.log_critical(f"thread {id} - Unknow method")

            ftp.disconnect()
            task = None

    except Exception as e: # just in case of
        Logger.log_critical(f"thread {id} - {e}")

    finally:
        if evt_done_main.is_set():
            evt_done_main.clear()
            main_loop.call_soon_threadsafe(lambda: evt_done_workers.set()) # run on main thread's loop
        shared_threads_working.value -= 1

    Logger.log_info(f"thread {id} - Stop ({threading.active_count()-2} left)") # main thread, async_input thread


def thread_pool(nb_threads, worker_args):
    shared_time_ref = multiprocessing.Value("d", time.time(), lock=False) # share var across all (threads in) process
    for id in range(nb_threads):
        threading.Thread(target=lambda:asyncio.run(async_worker(id, *worker_args, shared_time_ref))).start()