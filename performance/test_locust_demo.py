from locust import HttpUser, task, between, TaskSet
import json


# 1、创建locust.HttpUser子类
# 2、为用例加上@locust.task
# 3、使用@locust.task发送请求
# 4、指定wait_time属性
class MyUser(HttpUser):
    # host = 'http://192.168.1.155:9084'
    wait_time = between(0.1, 0.2)

    @task
    def get_lh_wafer(self):
        headers = {"SystemId": "all.akcome"}
        lh_wafer_url = 'http://192.168.1.155:9084/cut/wafer/getWaferIdList'
        payload = {"eqpCode": "切片机001", "carrierSn": "LH01"}

        r_lh_wafer = self.client.get(url=lh_wafer_url, headers=headers, json=payload)
        assert r_lh_wafer.status_code == 200
        lh_wafer_response_dict = json.loads(r_lh_wafer.text)
        # print('lh_wafer_response_dict: ', lh_wafer_response_dict)
        assert lh_wafer_response_dict.get('msg') == '成功'
