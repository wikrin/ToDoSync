import concurrent.futures


def threadPool(tasks: any, parlist: list) -> dict:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        sqlData: list = []
        response = pool.map(tasks, parlist)
    responses = list(zip(parlist, response))
    for cal, todo in responses:
        sqlData.append(
            {
                "epID": cal['epID'],
                "subject": cal['subject'],
                "EP": cal['EP'],
                "subject_id": cal['subject_id'],
                "status": todo['status'],
                "type": cal['type'],
            }
        )
    return sqlData
