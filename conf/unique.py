import logging
import os
from module.utils.calSQLite import *

logger = logging.getLogger(__name__)

PATH = 'data/temp.py'


class HttpMag(Config):
    def __init__(self, inc: str = 'MICROSOFT'):
        self.__inc = inc
        self.__sql = SQL()
        if os.path.exists(PATH):
            self.__privacy()
        super().__init__()
        self.CONFIG = self.take()

    def __privacy(self) -> bool:
        from data.temp import temp

        if self.__sql.add(temp, 'INSERT', 'init'):
            os.remove(PATH)
            return True
        else:
            raise

    def take(self) -> dict:
        js: dict = self.config
        __db = self.__sql.select('init', column=['KEY', self.__inc])
        for __kv in __db:
            js[__kv[0]] = __kv[1]
        return js
        # conf:dict = {**js, **__db}
        # return conf

    def ltd(self, keyname: list) -> dict:
        httpm = {key: self.CONFIG[key] for key in keyname}
        return httpm
