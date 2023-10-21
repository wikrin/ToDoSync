import requests
import json
import logging
from conf.unique import HttpMag, os
from module.utils.calSQLite import SQL

logger = logging.getLogger(__name__)
sql = SQL()


class Bangumi:
    def __init__(self, inc: str = 'BANGUMI'):
        self.__httpm = HttpMag(inc)
        self.__Authorization = {'Authorization': os.environ.get('BGM_TOKEN')}
        self.__headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'wikrin/ToDoSync (https://github.com/wikrin/ToDoSync)',
        }
        self.__headers.update(self.__Authorization)

    def put_ep(self, episode_id: str | int) -> int:
        try:
            resource = requests.put(
                f"https://api.bgm.tv/v0/users/-/collections/-/episodes/{episode_id}",
                headers=self.__headers,
                data=json.dumps({"type": 2}),
            )
            return resource.status_code

        except Exception as e:
            logger.error(f"错误详情：{e}")
            exit()

    def patch_eps(
        self, subject_id: str | int, episode_id: str | int, ep: str | int
    ) -> int:
        ep_first: int = int(episode_id) - int(ep) + 1
        epidlist: list = list(range(ep_first, int(episode_id)))
        __body = {
            "episode_id": epidlist,
            "type": 2,
        }
        try:
            resource = requests.put(
                f"https://api.bgm.tv//v0/users/-/collections/{subject_id}/episodes",
                headers=self.__headers,
                data=json.dumps(__body),
            )
            return resource.status_code

        except Exception as e:
            logger.error(f"错误详情：{e}")
            exit()

    def updata(self):
        resql = sql.select(
            'data',
            column=['subject_id', 'epID', 'EP', 'type'],
            where=[('status', 'completed'), ('type !', 2)],
        )
        for subid, epid, ep, type in resql:
            status:int = None
            match type:
                case 0:
                    status = self.put_ep(episode_id=epid)
                case 1:
                    status = self.patch_eps(
                        subject_id=subid,
                        episode_id=epid,
                        ep=ep,
                    )
                case 3:
                    status = self.patch_eps(
                        subject_id=subid,
                        episode_id=epid,
                        ep=ep,
                    )
            if status == 204:
                sql.initupdate(
                    table='data',
                    col_value=[('type', 2)],
                    where=[('epID', epid)],
                )
                logger.info(f"ID:{epid}进度完成")
            else:
                logger.error(status)
        logger.info("Bangumi点格子全结束")
