import os
import sys
import logging
import logging.config

sys.path.append(os.path.realpath("shared/"))
sys.path.append(os.path.realpath("tests/"))


class Logger(object):

    @staticmethod
    def log_debug(msg):
        logging.config.fileConfig("log.conf")
        logging.debug(msg)

    @staticmethod
    def log_info(msg):
        logging.config.fileConfig("log.conf")
        logging.info(msg)

    @staticmethod
    def log_warning(msg):
        logging.config.fileConfig("log.conf")
        logging.warning(msg)

    @staticmethod
    def log_error(msg):
        logging.config.fileConfig("log.conf")
        logging.error(msg)

    @staticmethod
    def log_critical(msg):
        logging.config.fileConfig("log.conf")
        logging.critical(msg)