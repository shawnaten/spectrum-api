import inspect
import os
import logging


def log_debug(message=""):
    debug = os.environ["DEBUG"]
    if debug:
        # 0 represents this line
        # 1 represents line at caller
        callerframerecord = inspect.stack()[1]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        logging.warn("{0}:{1}:{2}:{3}".format(
            info.filename,
            info.function,
            info.lineno,
            message
        ))
