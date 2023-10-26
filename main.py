import logging
from module import *

try:
    from dotenv import load_dotenv

    load_dotenv("conf/.env")
except:
    pass

logger = logging.getLogger(__name__)
if __name__ == "__main__":
    sql = SQL()
    graph = Graph()
    bgm = Bangumi()
    try:
        cal = graph.CalView()
        sql_dict = threadPool(graph.postTasks, cal)
        done = sql.add(sql_dict)
    except SystemExit as e:
        if e.code == 1:
            logger.info("没有获取到新的日程")
    finally:
        graph.getsks()
        bgm.updata()
