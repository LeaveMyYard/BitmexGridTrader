import os
import logging
import colorlog
import typing
from datetime import datetime


def init_logger(dunder_name: str, show_debug: bool = True) -> logging.Logger:
    log_format = (
        "%(asctime)s - "
        "%(name)s - "
        "%(funcName)s - "
        "%(levelname)s - "
        "%(message)s"
    )
    bold_seq = "\033[1m"
    colorlog_format = f"{bold_seq} " "%(log_color)s " f"{log_format}"
    colorlog.basicConfig(format=colorlog_format)
    logging.getLogger("tensorflow").disabled = True
    logger = logging.getLogger(dunder_name)

    if show_debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Note: these file outputs are left in place as examples
    # Feel free to uncomment and use the outputs as you like

    # Output full log
    # if not os.path.exists(os.path.join("log")):
    #     os.makedirs(os.path.join("log"))

    # fh = logging.FileHandler(os.path.join("log", "debug.log"), mode="a+")
    # fh.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(log_format)
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)

    return logger
