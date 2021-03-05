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

async def async_worker(evt_end, ftp_website, queue, lock):
    ftp = TalkToFTP(ftp_website)
    task = None

    functions = {"create_folder": ftp.create_folder,
                 "remove_file": ftp.remove_file,
                 "file_transfer": ftp.file_transfer,
                 "remove_folder": ftp.remove_folder}

    while not evt_end.is_set(): # true
        try:
            async with lock:
                if not queue.empty():
                    task = await queue.get()

            if not task:
                continue

            ftp.connect()

            if task[0] in functions:
                functions[task[0]](*task[1])
            else:
                Logger.log_critical(f"thread - Unknow method")

            ftp.disconnect()
            task = None

        except Exception as e:
            Logger.log_critical(f"thread - {e}")
            break

        finally:
            await asyncio.sleep(1)


def async_worker_launcher(evt_end, ftp_website, queue, lock):
    asyncio.run(async_worker(evt_end, ftp_website, queue, lock))


def thread_pool(nb_threads, evt_end, ftp_website, queue, lock):
    for _ in range(nb_threads):
        args = (evt_end, ftp_website, queue, lock)
        threading.Thread(target=async_worker_launcher, args=args).start()
