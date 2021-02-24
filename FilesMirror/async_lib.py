import asyncio
import sys
import contextlib
import threading
import time
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


async def async_worker(evt_end, evt_connect, evt_disconnect, ftp_website, queue, lock):
    # en vrai async, peut éventuellement faire :
    # si queue contient quelque chose, je le prend et m'exécute
    # si événement connect ou deconnect pop, je fais l'action équivalente
    # si événement fin pop, je me termine

    ftp = TalkToFTP(ftp_website)
    isLogged = False

    while not evt_end.is_set():
        if evt_connect.is_set():
            ftp.connect()
            evt_connect.unset()
            isLogged = True

        elif evt_disconnect.is_set():
            ftp.disconnect()
            evt_disconnect.unset()
            isLogged = False

        if not isLogged:
            await asyncio.sleep(1)
            continue

        async with lock:
            if not queue.empty():
                task = queue.get()

        # execute task

        await asyncio.sleep(1)


async def async_worker_bis(evt_end, ftp_website, queue, lock):
    ftp = TalkToFTP(ftp_website)
    task = None

    functions = {"create_folder": ftp.create_folder,
                 "remove_file": ftp.remove_file,
                 "file_transfer": ftp.file_transfer,
                 "remove_folder": ftp.remove_folder}

    while not evt_end.is_set(): # true
        try:
            print("     wait lock")
            async with lock:
                print("     get lock")
                if not queue.empty():
                    task = await queue.get()
            print("     release lock")

            if not task:
                continue

            ftp.connect()

            if task[0] in functions:
                functions[task[0]](*task[1])
            else:
                Logger.log_critical(f"thread - Unknow method")
            task = None

            ftp.disconnect()

        except Exception as e:
            Logger.log_critical(f"thread - {e}")
            break

        finally:
            await asyncio.sleep(1)
            # if await async_lib.event_wait(evt_end, 1):
            #     break

    print(f"close thread")


def async_worker_launcher(evt_end, ftp_website, queue, lock):
    asyncio.run(async_worker_bis(evt_end, ftp_website, queue, lock))


def thread_pool(nb_threads, evt_end, ftp_website, queue, lock):

    # control thread who multiplex (1 to n) evts connect & disconnect ?

    for _ in range(nb_threads):
        args = (evt_end, ftp_website, queue, lock)
        threading.Thread(target=async_worker_launcher, args=args).start()
