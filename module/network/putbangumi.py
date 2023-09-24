import requests
import json
import logging
from conf.unique import HttpMag
from module.utils.calSQLite import SQL

logger = logging.getLogger(__name__)
sql = SQL()


class Bangumi:
    def __init__(self, inc: str = 'BANGUMI'):
        self.__httpm = HttpMag(inc)
        self.__Authorization = {'Authorization': self.__httpm.CONFIG['Authorization']}
        self.TYPE: int = 2

    def updata(self):
        __headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'wikrin/ToDoSync (https://github.com/wikrin/ToDoSync)',
        }
        __headers.update(self.__Authorization)

        __body = {"type": self.TYPE}

        list = sql.select(
            'data', column=['epID'], where=[('status', 'completed'), ('type', 0)]
        )
        num: list = [id[0] for id in list]
        for id in num:
            try:
                resource = requests.put(
                    f"https://api.bgm.tv/v0/users/-/collections/-/episodes/{id}",
                    headers=__headers,
                    data=json.dumps(__body),
                )
                if resource.status_code == 204:
                    sql.initupdate(
                        table='data',
                        col_value=('type', self.TYPE),
                        where=[('epID', id)],
                    )
                    logger.info(f"ID:{id}进度完成")
                    return True
            except Exception as e:
                logger.error(f"错误详情：{e}")
                exit()

        logger.info("Bangumi点格子全结束")
