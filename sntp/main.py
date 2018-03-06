#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from sntp_server import SNTPServer

def main():
    logger = config_logging()
    logger.info("Started")
    server = SNTPServer()
    server.start()
    logger.info("Ended\n\n")


def config_logging():
    logger = logging.getLogger("sntp")
    logger.setLevel(logging.INFO)
    fileHandler = logging.FileHandler("sntp.log")
    formatter = logging.Formatter('%(asctime)s    %(name)s    %(levelname)s \n'
                                  '\t   %(message)s')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger


if __name__ == "__main__":
    main()