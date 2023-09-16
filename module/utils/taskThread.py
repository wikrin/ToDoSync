import concurrent.futures

def threadPool(tasks:any, parlist:list) -> dict:
    with concurrent.futures.ThreadPoolExecutor() as pool:
        sqlData:list = []
        response = pool.map(tasks, parlist)
        responses = list(zip(parlist, response))
        for calid, todoid in responses:
            sqlData.append({
                "epID" :calid['epID'],
                "subject" : calid['subject'],
                "calID" :calid['calID'],
                "todoID" : todoid['todoID'],
                "status": todoid['status'],
                "type" : 0
                })
    return sqlData
