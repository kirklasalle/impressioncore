import logging

def setup_rich_logging(*args, **kwargs):
    name = "dpa"
    level = logging.INFO
    for a in args:
        if isinstance(a, str):
            name = a
        elif isinstance(a, int):
            level = a
    if "name" in kwargs:
        name = kwargs["name"]
    if "level" in kwargs:
        level = kwargs["level"]
    logger = logging.getLogger(name)
    try:
        logger.setLevel(level)
    except Exception:
        pass
    return logger

def get_rich_logger(name="dpa"):
    return logging.getLogger(name)

def get_logger(name="dpa"):
    return logging.getLogger(name)
