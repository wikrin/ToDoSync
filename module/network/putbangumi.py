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

    def put_ep(self) -> int:
        try:
            resource = requests.put(
                f"https://api.bgm.tv/v0/users/-/collections/-/episodes/{self.episode_id}",
                headers=self.__headers,
                data=json.dumps({"type": 2}),
            )
            return resource.status_code

        except Exception as e:
            logger.error(f"错误详情：{e}")
            exit()

    def patch_eps(
        self, episode_id: int, ep: int = 1, type: int = 2
    ) -> tuple[int, list]:
        ep_first: int = episode_id - ep + 1
        epidlist: list = list(range(ep_first, episode_id + 1))
        __body = {
            "episode_id": epidlist,
            "type": type,
        }
        try:
            resource = requests.patch(
                f"https://api.bgm.tv/v0/users/-/collections/{self.subid}/episodes",
                headers=self.__headers,
                data=json.dumps(__body),
            )
            return (resource.status_code, epidlist)

        except Exception as e:
            logger.error(f"错误详情：{e}")
            exit()

    def patch_sub(self, type: int = 2) -> int:
        try:
            resource = requests.patch(
                f"https://api.bgm.tv/v0/users/-/collections/{self.subid}",
                headers=self.__headers,
                data=json.dumps({"type": type}),
            )
            return resource.status_code

        except Exception as e:
            logger.error(f"错误详情：{e}")
            exit()

    def updata(self):
        resql = sql.select(
            'data',
            column=['subject_id', 'epID', 'EP', 'type'],
            where=[('status', 'completed')],
        )
        logger.info(f"有{len(resql)}个进度更新")
        for self.subid, epid, ep, type in resql:
            status: tuple = (int, list)
            match type:
                case 0:  # 更新进度到当前话并标记为看过
                    sqlmsg = self.patch_eps(episode_id=epid, ep=ep)
                    if sqlmsg[0] == 204:
                        status = (self.patch_sub(), sqlmsg[-1])
                    infomsg:str = '看过'
                case 1:  # 更新进度到当前话
                    status = self.patch_eps(episode_id=epid, ep=ep)
                    infomsg:str = '看到'
                case 2:  # 更新当前话
                    # status = self.put_ep(episode_id=epid)
                    status = self.patch_eps(episode_id=epid)
                    infomsg:str = '看过'
                case 4:  # 搁置当前话并搁置番剧
                    sqlmsg = self.patch_eps(episode_id=epid, ep=1)
                    if sqlmsg[0] == 204:
                        status = (self.patch_sub(type=type), sqlmsg[-1])
                    infomsg:str = '搁置在'
            if status[0] == 204:
                sql.initupdate(
                    table='data',
                    col_value=[('status', 'done')],
                    where=[('epID >', status[-1][0]), ('epID <', status[-1][-1])],
                )
                logger.info(f"番剧ID{self.subid} {infomsg}EP{ep}")
            else:
                logger.error(status)
        logger.info("Bangumi进度更新结束")
