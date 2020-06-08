def requirements_list():
    list_of_req = []
    with open('requirements.txt') as req:
        for line in req:
            list_of_req.append(line)

    return list_of_req