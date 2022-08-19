import random
import datetime
from locust import HttpUser, task, between


# 1、创建locust.HttpUser子类
# 2、为用例加上@locust.task
# 3、使用@locust.task发送请求
# 4、指定wait_time属性
class MyUser(HttpUser):
    # host = 'http://192.168.1.155:9084'
    wait_time = between(0.1, 0.2)

    @task
    def add_mo(self):
        wo_code_str = 'WO' + str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))[2:] + '%06d' % random.randint(1,
                                                                                                                 99999)
        print('wo_code_str: ', wo_code_str)
        url = "http://192.168.233.32:9002/webservice/prod"
        payload = '<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\r\n<soap:Body>\r\n<addMO xmlns=\"http://sap.webservice.client.mes.microservice.tfinfo.cn\">\r\n    <param>\r\n      {\r\n    \"REQUEST\": {\r\n        \"I_HEAD\": {\r\n            \"WORKORDERNO\": \"%s\",\r\n            \"PRODUCTCODE\": \"s.01.001.0445\",\r\n            \"BOMID\": \"BOMBOMBOM0606\",\r\n            \"BOMVER\": \"0\",\r\n            \"STATUS\": \"1\",\r\n            \"ORDERTYPE\": \"ZP08\",\r\n            \"MOTYPE\": \"LX1\",\r\n            \"RELEASEDATE\": \"20220525\",\r\n            \"SCHEDULEDSTARTDATE\": \"20220525\",\r\n            \"SCHEDULEDDUEDATE\": \"20220525\",\r\n            \"PRIORITY\": \"99\",\r\n            \"PROCESSPLANCODE\": \"50000020\",\r\n            \"PROCESSPLANREVISION\": \"01\",\r\n            \"PRODUCTIONQTY\": 22.000,\r\n            \"UOMID\": \"PCS\",\r\n            \"USERCODE\": \"AB_RENA\",\r\n            \"USERNAME\": \"AB_RENA\",\r\n            \"CREATEDATE\": \"20220519\",\r\n            \"REMARKS\": \"test\",\r\n            \"BATCHNO\": \"0\",\r\n            \"PROJECTNO\": \"00000004\",\r\n            \"BILLRESOURCE\": \"2\",\r\n            \"SALESORDER\": \"6200000051\",\r\n            \"SALESORDERITEM\": 10,\r\n            \"CUSTOMERNO\": \"SH0099\",\r\n            \"FACTORYNO\": \"1012\",\r\n            \"ERPMOLINENO\": \"\",\r\n            \"ZYL01\": \"\",\r\n            \"ZYL02\": \"\",\r\n            \"ZYL03\": \"\",\r\n            \"ZYL04\": \"\",\r\n            \"ZYL05\": \"\"\r\n        },\r\n        \"I_ITEM\": {\r\n            \"ITEM\": [\r\n                {\r\n                    \"RSPOS\": 1,\r\n                    \"POSTP\": \"L\",\r\n                    \"IDNRK\": \"BOMBOMBOM0606\",\r\n                    \"MAKTX\": \"TEST\",\r\n                    \"BDMNG\": 10,\r\n                    \"MEINS\": \"片\",\r\n                    \"BWART\": \"Z61\",\r\n                    \"CHARG\": \"\",\r\n                    \"ZYL06\": \"\",\r\n                    \"ZYL07\": \"\",\r\n                    \"ZYL08\": \"\",\r\n                    \"ZYL09\": \"\",\r\n                    \"ZYL10\": \"\"\r\n                },\r\n            ]\r\n        }\r\n    }\r\n}\r\n      </param>\r\n        </addMO>\r\n    </soap:Body>\r\n</soap:Envelope>' \
                  % wo_code_str
        headers = {
            'Content-Type': 'application/json'
        }

        response = self.client.request("POST", url, headers=headers, data=payload.encode('utf-8'))
        print('response_code: ', response.status_code)
        assert response.status_code == 200
