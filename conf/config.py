import json
import logging
import threading

PATH = "conf/config.json"

logger = logging.getLogger(__name__)


class Config:
    __all__ = ["TEMPPATH", "DATABASEPATH", "DAY", "config"]

    _instance_lock = threading.Lock()

    def __new__(cls, args=('null'), **kwargs):
        if not hasattr(cls, 'instance_dict'):
            Config.instance_dict = {}

        if str(args[0]) not in Config.instance_dict.keys():
            with Config._instance_lock:
                _instance = super().__new__(cls)
                Config.instance_dict[str(args[0])] = _instance
        return Config.instance_dict[str(args[0])]

    # def __new__(cls, *args):
    #     if not hasattr(cls, '_instance'):
    #         _instance = super().__new__(cls)
    #     return _instance

    def __init__(self) -> dict:
        self.config: dict = self.load()

        self.TEMPPATH: str = self.config['tempPath']
        self.DATABASEPATH: str = self.config['databasePath']
        self.DAY: int = int(self.config['day'])

    def load(self) -> dict:
        logger.info(f"读取{PATH}文件")
        with open(PATH, "r", encoding="utf-8") as js:
            __config: dict = json.load(js)
        logger.info("Done")
        return __config

    def save(self, config: dict) -> bool:
        if not config:
            config = self.load()
        with open(PATH, "w", encoding="utf-8") as js:
            json.dump(config, js, indent=2, sort_keys=True, ensure_ascii=False)
        logger.info("Done")
        return True
