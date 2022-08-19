import requests
import json


def get_ticket():
    url = 'http://192.168.1.127:9997/api/usercenterdev/userService/login'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Authorization": "",
        "Content-Length": "136",
        "Content-Type": "application/json",
        "Cookie": "systemId=; ticket=",
        "Host": "192.168.1.127:9997",
        "lang": "zh",
        "Origin": "http://192.168.1.127:9997",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://192.168.1.127:9997/AKCOMEMESOP/operate",
        "SystemId": "all.akcome",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4878.0 Safari/537.36"
    }

    data = {
        "requestId": "918V02VSGTTPB9CFAB3VD5ORQHPSSKAT",
        "systemId": "all.akcome",
        "userNo": "WLH001",
        "userPass": "e10adc3949ba59abbe56e057f20f883e"
    }
    r = requests.post(url, headers=headers, data=json.dumps(data))
    response_str = r.text  # json串
    responsedict = json.loads(response_str)  # 转字典
    print("responsedict:", responsedict)
    login = responsedict.get("login")
    ticket = responsedict.get("ticket")
    print("login:", login)
    # print("ticket:", ticket)
    return ticket


if __name__ == '__main__':
    ticket = get_ticket()
    print("ticket:", ticket)
