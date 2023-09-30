import requests
import logging
import json
from datetime import datetime, timedelta
import re
from urllib import parse
from module.utils.calSQLite import SQL
from conf.unique import HttpMag

logger = logging.getLogger(__name__)
sql = SQL()


class Graph:
    # def __new__(cls):
    #     if not hasattr(cls, '_instance'):
    #         cls._instance = super(Graph,cls).__new__(cls)
    #     return cls._instance

    def __init__(self, inc: str = 'MICROSOFT'):
        self.__httpm = HttpMag(inc)
        if self.check():
            self.__CAL = self.calID()
            self.__date = self.confine()
            self.__Authorization = {
                'Authorization': self.__httpm.CONFIG['Authorization']
            }

    # __headers.update({
    #     "Prefer" : config.config['Prefer']
    # })

    def CalView(self) -> list:
        __headers = {"Content-Type": "application/json"}
        __headers.update(self.__httpm.ltd(['Authorization', 'Prefer']))
        # __headers.update(self.__httpm.ltd(['Authorization', 'Prefer']))

        # seq = ['Authorization', 'Prefer']

        logger.info("获取日历事件列表")
        try:
            calender = requests.get(
                f"https://graph.microsoft.com/v1.0/me/calendars/{self.__CAL}/calendarView",
                params={"startDateTime": self.__date[0], "endDateTime": self.__date[1]},
                headers=__headers,
            )
            event = calender.json()['value']
        except Exception as e:
            logger.exception(f"日历事件列表获取失败:{event}\错误详情:{e}")
            exit()
        else:
            # event = json.dumps(calender.json()["value"], indent=2, sort_keys=True, ensure_ascii=False)
            if calender.status_code == 200:
                calenderlist: list = [
                    {
                        "subject": fanlist['subject'],
                        "epID": int(re.sub(r'\D', "", fanlist['bodyPreview'])),
                        "calID": fanlist['id'],
                        "startTime": fanlist['start']['dateTime'],
                        "endTime": fanlist['end']['dateTime'],
                    }
                    for fanlist in event
                    if len(
                        sql.select(
                            'data',
                            column=['*'],
                            where=[
                                ('epID', int(re.sub(r'\D', "", fanlist['bodyPreview'])))
                            ],
                        )
                    )
                    == 0
                ]

                logger.info(f"新获得{len(calenderlist)}个列表")
                if len(calenderlist) == 0:
                    return exit(1)
                return calenderlist
            else:
                logger.error(f"日历事件列表请求失败:{event}")
                exit()

    def confine(self) -> tuple[str, str]:
        today: datetime = datetime.utcnow() - timedelta(hours=16)
        morrow: datetime = today + timedelta(days=self.__httpm.DAY)
        start: str = datetime.strftime(
            datetime.strptime(self.__httpm.CONFIG['start'], "%H:%M:%S")
            - timedelta(hours=8),
            "%H:%M:%S",
        )
        end: str = datetime.strftime(
            datetime.strptime(self.__httpm.CONFIG['end'], "%H:%M:%S")
            - timedelta(hours=8),
            "%H:%M:%S",
        )

        starttime: str = f"{today.strftime('%Y-%m-%d')}T{start}"
        endtime: str = f"{morrow.strftime('%Y-%m-%d')}T{end}"
        return (starttime, endtime)

    def check(self) -> bool:
        checktoken = requests.get(
            "https://graph.microsoft.com/v1.0/me/calendars",
            headers={'Authorization': self.__httpm.CONFIG['Authorization']},
        )
        if checktoken.status_code == 200:
            logger.info("token时效期内")
            return True
        elif checktoken.status_code == 401:
            logger.info("token失效")
            tokens = {"refresh_token": self.__httpm.CONFIG['refresh_token']}
            logger.info("读取refresh ...")

        self.__body = {
            'grant_type': 'refresh_token',
            'redirect_uri': "http://localhost/myapp/",
        }

        self.__body.update(
            self.__httpm.ltd(["client_id", "scope", "client_secret", "refresh_token"])
        )

        logger.info("以refresh token刷新token")
        retoken = requests.post(
            "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=parse.urlencode(self.__body),
        )
        if retoken.status_code == 200:
            logger.info("token刷新请求成功")
            tokendict = retoken.json()
            jslist: dict = {"Authorization": "Bearer " + tokendict['access_token']}
            if "refresh_token" in tokendict:
                jslist['refresh_token'] = tokendict['refresh_token']
            msft = {'MICROSOFT': jslist}
            logger.info("正在保存")
            if sql.add(rule=msft, table='init'):
                self.__httpm.__init__()
                logger.info("保存成功")
                return True
        else:
            logger.info("token刷新失败")
            raise

    def ListID(self) -> str:
        self.__headers = {"Content-Type": "application/json"}
        self.__headers.update(self.__Authorization)
        logger.info("获取列表ID")

        lists = requests.get(
            "https://graph.microsoft.com/v1.0/me/todo/lists", headers=self.__headers
        )
        todolist = lists.json()['value']

        for name in todolist:
            if name["displayName"] == "任务":
                todoid: str = name["id"]
                logger.debug(f"ID为:{todoid}")
            return todoid

    def postTasks(self, dict: dict, id: str = None):
        if id == None:
            id = self.ListID()
        taskbody: dict = {
            "title": dict['subject'],
            "startDateTime": {
                "dateTime": dict['startTime'],
                "timeZone": "Asia/Shanghai",
            },
            "dueDateTime": {"dateTime": dict['endTime'], "timeZone": "Asia/Shanghai"},
            "importance": "normal",
            "isReminderOn": "False",
            "linkedResources": [
                {
                    "webUrl": f"https://bgm.tv/ep/{dict['epID']}",
                    "applicationName": "Bangumi",
                }
            ],
        }
        logger.info(f"正在创建任务:{dict['subject']}")
        try:
            task = requests.post(
                f"https://graph.microsoft.com/v1.0/me/todo/lists/{id}/tasks",
                headers=self.__headers,
                data=json.dumps(taskbody),
            )
        except Exception as e:
            logger.exception(e)
        if task.status_code == 201:
            todo = task.json()
            logger.debug(todo)
            logger.info(f"{todo['title']},完成")
            return {"todoID": todo['id'], "status": todo['status']}
        else:
            logger.info(f"{todo}['title'],失败")

    def getsks(self) -> list:
        list = sql.select(
            'data', column=['epID'], where=[('status', 'notStarted'), ('type', 0)]
        )
        num: list = [id[0] for id in list]
        tasks = requests.get(
            f"https://graph.microsoft.com/v1.0/me/todo/lists/{self.ListID()}/tasks",
            headers=self.__Authorization,
        )
        taskjs = tasks.json()['value']
        tasksup: list = [
            [
                ('status', task['status']),
                ('epID', int(re.sub(r'\D', "", task['linkedResources'][0]['webUrl']))),
            ]
            for task in taskjs
            if int(re.sub(r'\D', "", task['linkedResources'][0]['webUrl'])) in num
        ]
        for up in tasksup:
            sql.initupdate('data', up[0], [up[1]])
        return tasksup

    def calID(self) -> str:
        checktoken = requests.get(
            "https://graph.microsoft.com/v1.0/me/calendars",
            headers={'Authorization': self.__httpm.CONFIG['Authorization']},
        )
        for id in checktoken.json()['value']:
            if id['name'] == self.__httpm.CONFIG['calName']:
                calid: str = id['id']
        return calid
