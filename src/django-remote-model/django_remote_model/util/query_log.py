import logging
import json

logger = logging.getLogger('polyana_web')

def __log_query(header_logger, contents_logger, func_name, url, r, data=None):
    header_logger("{}: URL: {}".format(func_name, url))
    if data is not None:
        contents_logger(">" * 10)
        contents_logger(json.dumps(data, indent=2, ensure_ascii=False))
    try:
        contents_logger("<" * 10)
        contents_logger(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except ValueError:
        logger.debug("Result has no JSON")


def info(func_name, url, r, data=None):
    __log_query(logger.info, logger.debug, func_name, url, r, data)

def error(func_name, url, r, data=None):
    __log_query(logger.error, logger.error, func_name, url, r, data)

