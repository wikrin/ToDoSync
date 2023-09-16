from module import *
from module.graph import Graph
from module.utils.calSQLite import SQL
from module.network.putbangumi import Bangumi

logger = log.getlogger(__name__)
if __name__ == "__main__":
    sql = SQL()
    graph = Graph()
    bgm = Bangumi()
    try:
        cal = graph.CalView()
        test = threadPool(graph.postTasks, cal)
        done = sql.add(test)
    except SystemExit as e:
        if e == 1:
            logger.info("没有获取到新的日程")
    finally:
            graph.getsks()
            bgm.updata()