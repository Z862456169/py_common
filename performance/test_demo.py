import requests


def test_get_baidu():
    resp = requests.get('https://www.baidu.com')
    status_code = resp.status_code
    print("status_code: ", status_code)
    result = resp.text
    print("result: ", result)



if __name__ == '__main__':
    test_get_baidu()
