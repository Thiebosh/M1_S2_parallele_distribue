from directory_manager import DirectoryManager
from get_parameters import get_user_parameters
import asyncio
from logger import Logger
from sys import version_info


if __name__ == "__main__":
    # get parameters from command line
    ftp_website, local_directory, max_depth, refresh_frequency, nb_multi, excluded_extensions = get_user_parameters()

    # init directory manager with local directory and maximal depth
    directory_manager = DirectoryManager(ftp_website, local_directory, max_depth, excluded_extensions)

    # launch the synchronization
    try:
        if version_info < (3,7):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(directory_manager.synchronize_directory(refresh_frequency, nb_multi))
            loop.close()
        else:
            asyncio.run(directory_manager.synchronize_directory(refresh_frequency, nb_multi))
    except KeyboardInterrupt:
        Logger.log_info("Unnecessary keyboard interrupt : simply press enter")
    except Exception as e: # just in case of
        Logger.log_critical(e)
    finally:
        Logger.log_info("Close program")
