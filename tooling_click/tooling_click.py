import requests
from urllib import parse


def tooling_click(value):
    headers = {
        "Authorization": "6026b6cdcdaa4ce5b67cebcfdd437a81192.168.30.195,192.168.1.153",
        "SystemId": "all.silicon",
        'Accept-Encoding': 'gzip, deflate'
    }
    url_value = '%s' % {"requestId": "J2G4DE415COJQ2LMQKTVJCCKHETHBQ5R", "id": value}
    url_encode = parse.quote(url_value)
    print("url_value:", url_value)
    url = "http://192.168.1.153:9996/api/mesbasictms/toolingBackUp/initToolingBackUpDetail?" + url_encode
    # url = "http://192.168.1.153:9996/api/mesbasictms/toolingBackUp/initToolingBackUpDetail?%7B%22requestId%
    # 22%3A%22J2G4DE415COJQ2LMQKTVJCCKHETHBQ5R%22%2C%22id%22%3A%227a470ea3c9414d538695f4e9cf0851f9%22%7D"

    res = requests.get(url=url, headers=headers)
    print("result: " + res.text)


def open_tooling():
    with open('./tooling1.txt', mode='r', encoding='utf-8') as file:
        list_id = file.readlines()
    print("list_id:", list_id)
    for data in list_id:
        value = data.strip('\n')
        print("id:", value)
        tooling_click(value)


if __name__ == '__main__':
    # value = "db980daae5cf422ab752474adce81de8"
    # tooling_click(value)
    open_tooling()
