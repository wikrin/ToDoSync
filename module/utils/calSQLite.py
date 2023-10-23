import sqlite3
import threading
import logging
from conf.config import Config

logger = logging.getLogger(__name__)
config = Config()


class SQL:
    _instance_lock = threading.Lock()

    def __new__(cls, str: str = 'null'):
        if not hasattr(cls, 'instance_dict'):
            Config.instance_dict = {}

        if str not in Config.instance_dict.keys():
            with Config._instance_lock:
                _instance = super().__new__(cls)
                Config.instance_dict[str] = _instance
        return Config.instance_dict[str]

    def __init__(self):
        self.conn = sqlite3.connect(config.DATABASEPATH, check_same_thread=False)
        # self.conn.row_factory = SQL.dict_factory
        self.cur = self.conn.cursor()
        with self.conn:
            self.cur.executescript(
                '''
                CREATE TABLE IF NOT EXISTS data(
                    `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
                    `epID` INTEGER NOT NULL UNIQUE,
                    `subject` TEXT NOT NULL,
                    `EP` INTEGER NOT NULL,
                    `subject_id` INTEGER NOT NULL,
                    `status` TEXT NOT NULL,
                    `type` INTEGER NULL);
                                
                CREATE TABLE IF NOT EXISTS init(
                    `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
                    `KEY` TEXT NOT NULL UNIQUE,
                    `MICROSOFT` TEXT,
                    `BANGUMI` TEXT)'''
            )

    __all__ = ['add', 'select', 'update']

    def dict_factory(cursor, row):
        d = {}
        d[row[0]] = row[1]
        # for index, col in enumerate(cursor.description):
        #     d[col[0]] = row[index]
        return row

    def DDtO(self, rule: (dict | list), out: str = 'IN') -> list:
        if type(rule) == list:  # 如果是列表要先遍历列表结构
            if type(rule[0]) == dict:
                # 将字典key，value分别打包为元组，再将这两个元组打包成一个列表然后添加进列表数据结构：列表[列表[元组(), 元组()],列表[元组(), 元组()], ...]
                self.__key_value: list = [
                    [tuple(sqldict), tuple(sqldict.values())] for sqldict in rule
                ]

                return self.__key_value

            else:  # 传入数据结构不是list-dict则输出日志
                logger.error(f"参数错误,数据结构:{type(rule)}-{type(rule[0])}不受支持")

        elif (
            out == 'IN'
            and type(rule) == dict
            and type(rule[list(rule.keys())[0]]) == dict
        ):
            self.__key_value: list = [
                [("KEY", inc), (key, rule[inc][key])]
                for inc in rule
                for key in rule[inc]
            ]

            return self.__key_value

        elif (
            out == 'UP'
            and type(rule) == dict
            and type(rule[list(rule.keys())[0]]) == dict
        ):
            self.key_value: list = [
                {inc: (key, rule[inc][key])} for inc in rule for key in rule[inc]
            ]

            return self.__key_value

        else:
            logger.error(f"参数错误,类型:{type(rule)}-{type(rule[list(rule.keys())[0]])}不受支持")
            exit()

    def add(
        self, rule, method: str = ('INSERT'), table: str = ('data')
    ) -> (
        bool
    ):  # 传入参数，data,要处理的数据：list或dict类型，method,使用的方法:INSERT 插入，REPLACE 替换，table:要操作的表
        key_value = self.DDtO(rule, 'IN')
        for tup in key_value:
            with self.conn:
                try:
                    self.cur.execute(
                        f'''{method} INTO {table} {tup[0]} VALUES {tup[1]}'''
                    )

                except sqlite3.IntegrityError:
                    if self.initupdate(
                        table='init',
                        col_value=[(tup[0][1], tup[1][1])],
                        where=[(tup[0][0], tup[1][0])],
                    ):
                        continue
                    else:
                        raise
        return True

    # rule
    def initupdate(
        self, table: str, col_value: list[tuple], where: list[tuple] = [('epID', 0)]
    ) -> bool:
        where_clause: str = ' WHERE 1=1 '
        params = []
        upset = []
        for col_val in col_value:
            colval = f"`{col_val[0]}` = '{col_val[1]}'"
            upset.append(colval)
        query = f"UPDATE {table} SET {', '.join(upset)}"
        for clause in where:
            where_clause += f'AND {clause[0]}=?'
            params.append(clause[1])
            with self.conn:
                self.cur.execute(query + where_clause, params)
                return True

    def select(
        self, table: str, column: list[str] = ['MICROSOFT'], where: list[tuple] = [()]
    ) -> list:
        # 参数table:表名，column:查询多个列将列名以字符串类型放入一个元组，放入的顺序决定返回字典的键和值
        # where:查询条件 条件的键值以元组形式放入列表中 [0]为查询键，[1]为查询值
        where_clause: str = ' WHERE 1=1 '
        params = []
        if where[0]:
            for clause in where:
                where_clause += f'AND {clause[0]}=?'
                params.append(clause[1])
        query = f'SELECT {", ".join(column)} FROM {table}' + where_clause
        with self.conn:
            try:
                lan = self.cur.execute(query, params)
            except sqlite3.OperationalError:
                logger.warning(f"库中不存在列:{column}")
        # tuple = lan.fetchone()
        db: list[tuple] = lan.fetchall()
        return db
