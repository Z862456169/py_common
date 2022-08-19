import requests
import datetime
import json
import random
import time


def request_material():
    wl_lst = []
    wl_dict = {
        "MATNR": "C011100001",
        "WERKS": "1012",
        "MAKTX": "4寸玻璃厚度0.2mm,平边32±1mm，AF32",
        "ZXMMS": "",
        "MATKL": "C0111",
        "MTART": "Z003",
        "MHDHB": "1825",
        "MHDRZ": "913",
        "IPRKZ": "D",
        "UMREN3": 0,
        "MSEHT3": "",
        "BSTME": "",
        "UMREZ3": 0,
        "UMREN": 0,
        "MSEHT1": "",
        "AUSME": "",
        "UMREZ": 0,
        "MSEHT2": "PCS",
        "MEINS": "PCS",
        "ERNAM": "AB_YOLLY",
        "ERSDA": "20220615",
        "AENAM": "AB_YOLLY",
        "LAEDA": "20220615",
        "ZORIGIN": "SAP",
        "ZSTATUS": "",
        "ZPUTINPLACE": "3",
        "ZCOUNTWAY": "1",
        "XCHAR": "X",
        "ZSFJY": "X",
        "ZTDWL": "",
        "ZHXTX": "",
        "ZCCTJ": "",
        "EISBE": 50.000,
        "Z_VENDOR": "X",
        "Z_VENDORLOT": "X",
        "Z_CUSTOMER": "X",
        "Z_CUSTOMERLOT": "X",
        "Z_PD": "X",
        "Z_VFDAT": "X",
        "Z_WEDAT": "X",
        "Z_WAFERID": "X",
        "Z_EXTBATCH": "X",
        "Z_GROSSDIE": "X",
        "Z_CUSTWAFERID": "",
        "Z_OURLOT": "",
        "Z_OURWAFERID": "",
        "Z_REELID": "",
        "Z_GOODDIE": "",
        "Z_REMANENTDIE": "",
        "Z_BIN": "",
        "Z_BINCLASS": "",
        "Z_LOTTYPE": "",
        "Z_ORDERTYPE": "",
        "Z_PACKAGE": "",
        "Z_SONUMBER": "",
        "Z_SOITEM": "",
        "ERPDEVICE": "C011100001",
        "ZYL01": "",
        "ZYL02": "",
        "ZYL03": "",
        "ZYL04": "",
        "ZYL05": "",
        "ZYL06": "",
        "ZYL07": ""
    }
    print("MATNR: ", wl_dict.get('MATNR'))
    for _ in range(10):
        wl_dict['MATNR'] = 'stest' + str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))[
                                     2:] + '%06d' % random.randint(1, 99999)
        wl_lst.append(wl_dict)
        print("wl_lst_len:%03s, wl_lst:%s" % (len(wl_lst), wl_lst))
    url = "http://192.168.233.32:9002/webservice/prod"
    payload = '<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\n    <soap:Body>\n        <materialDetail xmlns=\"http://sap.webservice.client.mes.microservice.tfinfo.cn\">\n            <param>\n{\n      \"REQUEST\": {\n        \"I_INPUT\": %s    }\n}\n      </param>\n        </materialDetail>\n    </soap:Body>\n</soap:Envelope>' \
              % wl_lst
    headers = {'Content-Type': 'text/xml; charset=utf-8'}
    start_time = time.time()
    response = requests.request("POST", url, headers=headers, data=payload.encode('utf-8'))
    assert response.status_code == 200
    print(response.text)
    res_data = json.loads(response.text.split('return')[1].split('<')[0].split('>')[1])
    print(type(res_data))
    print(res_data)
    end_time = time.time()
    delta_time = end_time - start_time
    print('delta_time: ', delta_time)


if __name__ == '__main__':
    # add_mo()
    request_material()
