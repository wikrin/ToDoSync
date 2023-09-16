import logging, logging.config

def getlogger(name:str='root'):
    path = "conf/log.conf"
    with open(path, 'r', encoding='utf-8') as conf:
        logging.config.fileConfig(conf, disable_existing_loggers = False)
    logger = logging.getLogger(name)
    return logger
