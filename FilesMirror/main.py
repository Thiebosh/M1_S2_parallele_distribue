from directory_manager import DirectoryManager
from get_parameters import get_user_parameters
import asyncio


async def main(event_end):
    # get parameters from command line
    ftp_website, local_directory, max_depth, refresh_frequency, excluded_extensions = get_user_parameters()

    # init directory manager with local directory and maximal depth
    directory_manager = DirectoryManager(ftp_website, local_directory, max_depth, excluded_extensions)

    # start event_end getter thread

    # launch the synchronization
    await asyncio.gather(directory_manager.synchronize_directory(refresh_frequency),)


if __name__ == "__main__":
    event_end = asyncio.Event()
    try:
        if hasattr(asyncio, "run"):
            asyncio.run(main(event_end))

        else:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main(event_end))
            loop.close()

    except KeyboardInterrupt:
        print("get extinction signal")

    finally:
        event_end.set()
        print("close program")
