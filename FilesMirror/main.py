from directory_manager import DirectoryManager
from get_parameters import get_user_parameters
import asyncio


async def main():
    # get parameters from command line
    ftp_website, local_directory, max_depth, refresh_frequency, excluded_extensions = get_user_parameters()

    # init directory manager with local directory and maximal depth
    directory_manager = DirectoryManager(ftp_website, local_directory, max_depth, excluded_extensions)

    queue = asyncio.Queue()

    # launch the synchronization
    await asyncio.gather(directory_manager.synchronize_directory(refresh_frequency, queue),)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        print("close program")
