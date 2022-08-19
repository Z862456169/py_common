import requests
import json


class Mes(object):
    def __init__(self):
        self.ip_port = 'http://192.168.1.150:9084'
        self.ip_port_test = 'http://192.168.70.88:9084'
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4878.0 Safari/537.36"
        }

    def get_requests(self, url, payload):
        '''
        发起get请求
        :param url: 传入url，string
        :param payload: 传入请求体，dict
        :return:
        '''
        r = requests.get(url, headers=self.headers, json=payload)
        return r.text

    def post_requests(self, url, data):
        '''
        发起post请求
        :param url: 传入url，string
        :param data: 传入请求体，json
        :return:
        '''
        r = requests.post(url, headers=self.headers, data=data)
        return r.text

    def get_lh_wafer(self):
        '''
        获取料盒 WaferID
        :return:
        '''
        url = self.ip_port + '/cut/wafer/getWaferIdList'
        payload = {
            "eqpCode": "切片机001",
            "carrierSn": "LH322"
        }
        return self.get_requests(url, payload=payload)

    def post_load_cassette_take_off(self):
        '''
        上料cassette需要拿走接口
        :return:
        '''
        url = self.ip_port + '/track/cassette/release'
        data = {
            "carrierSn": "HL266"
        }
        return self.post_requests(url, data=json.dumps(data))


if __name__ == '__main__':
    mes = Mes()
    result = mes.get_lh_wafer()
    print(result)
