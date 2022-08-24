import requests
import json
from getticket import get_ticket
import urllib.parse
from connect_oracle import ConnectOracle
import datetime


class Base(object):
    def __init__(self):
        self.ip_port = 'http://192.168.1.127:9997'
        self.headers = {
            "Authorization": get_ticket(),
            "SystemId": "all.akcome"
        }
        self.decimal_code_result = None
        self.cassette_code_result = None

    def cut_wafer(self):
        '''
        操作切片
        :return: str 切片成功信息
        '''
        url = self.ip_port + '/api/mesakcometest/cut/wafer/manage/check/in'
        data_body = {
            "woId": "GCQGTIBCFM3KD43ATMN3ETQD2EH7E3P5",
            "woCode": "WO202208240001",
            "waferCode": "GPWL-01",
            "waferSpec": "210硅片",
            "siliconWaferLotNo": "",
            "eqpCode": "切片机001",
            "carrierSn": "LH01",
            "totalQty": "2",
            "waferSizeName": "对角线:200mm边长:156*156mm",
            "waferId": "5f11042dcb7b48c299818f2a18e4bafa",
            "siliconWaferLotList": [
                "GPWL-01.220824.002"
            ],
            "requestId": "ER6FUCSEL77MMU0371KDQA6OUSA8SKNB"
        }
        r = requests.post(url=url, headers=self.headers, json=data_body)
        response_dict = json.loads(r.text)
        print('cut_wafer:', response_dict)
        assert response_dict.get('msg') == "成功"
        return response_dict.get('msg')

    def get_whole_wafer(self):
        '''
        获取整片wafer的十进制码
        :return: list 整片wafer十进制码, [No1, No2]
        '''
        # 获取最新的切片信息
        cut_url_value = '{"woCode":"","siliconWaferLotNo":"","carrierSn":"","finishFlag":"N","pageSize":15,"pageNo":1,"requestId":"COHDM8DU5L6MHRVFGBM2OD15B5MJVRU1"}'
        cut_url_byte = urllib.parse.quote(cut_url_value)  # 将字符串进行url编码
        cut_url = self.ip_port + '/api/mesakcometest/cut/wafer/manage/findList?' + cut_url_byte
        response_dict = json.loads(requests.get(url=cut_url).text)  # 转字典
        wafer_id = response_dict.get('rows')[0].get('id')
        # print('cutWaferManageId:', wafer_id)

        # 获取整片长码
        whole_url_value = '{"cutWaferManageId": "%s", "cutFlag": "N", "type": "Whole","status": "Normal","outputFlag": "", "pageNo": 1, "pageSize": 15, "requestId": "OKHML0I8C13IF73PBJ4E2OL5M7C54J9S"}' % wafer_id
        whole_url_byte = urllib.parse.quote(whole_url_value)  # 将字符串进行url编码
        whole_url = self.ip_port + '/api/mesakcometest/cut/wafer/manage/findWaferList?' + whole_url_byte
        whole_response_dict = json.loads(requests.get(url=whole_url).text)  # 转字典
        whole_wafer_no = whole_response_dict.get('rows')  # 列表
        whole_wafer_no_list = []  # 长码列表
        for index, no in enumerate(whole_wafer_no):
            whole_wafer_no_list.append(whole_wafer_no[index].get('waferNo'))
        # print('whole_wafer_no_list:', whole_wafer_no_list)

        # 操作数据库获取整片十进制码
        ten_wafer_no = []
        for wafer_no in whole_wafer_no_list:
            sql = "SELECT ENTIRE_DECIMAL_CODE,WAFER_NO FROM MESAKCOMEDEV.MC_BASE_WAFER_INFO WHERE PARENT_ID IN (SELECT ID FROM MESAKCOMEDEV.MC_BASE_WAFER_INFO WHERE WAFER_NO IN ('%s'))" % wafer_no
            con = ConnectOracle()
            decimal_code = con.connect_oracle(sql)
            ten_wafer_no.append(decimal_code)
            # print('get_whole_wafer:', decimal_code)
        print('get_whole_wafer_list:', ten_wafer_no)
        return [ten_wafer_no[0][0][0], ten_wafer_no[0][1][0], ten_wafer_no[1][0][0], ten_wafer_no[1][1][0]]

    def get_cassette_old(self):
        '''
        获取cassette编号
        :return: list cassette编号 [No1, No2, No3]
        '''
        # 新增cassette
        cassette_url = self.ip_port + '/api/mesbasicakcometest/carrier/addCarrier'
        data_body = {
            "carrierKind": "FB",
            "startCode": "1",
            "inputCount": "4",
            "cartypeCode": "HL-s",
            "cartypeName": "HL-s",
            "cartypeId": "1e29054700274169a0caa9948bd8c2ff",
            "prodorgType": "WSH",
            "prodorgId": "db49bec4f79842198d4feba76e6c8fed",
            "prodorgCode": "01",
            "prodorgName": "一期车间",
            "manufactureDate": str(datetime.date.today()),
            "model": "",
            "simpleCode": "HL-s",
            "requestId": "O9DB5H30BBGQMJDP04ES80JMMJV986FM"
        }
        r = requests.post(url=cassette_url, headers=self.headers, json=data_body)
        response_dict = json.loads(r.text)
        assert response_dict.get('msg') == '保存成功'
        cassette_ids = response_dict.get('data')
        # print('cassette_ids:', cassette_ids)

        # 启用cassette
        start_using_url = self.ip_port + '/api/mesbasicakcometest/carrier/updActiveFlag'
        data_body_using = {
            "ids": cassette_ids,
            "activeFlag": "Y",
            "requestId": "EV10O8RJGHHFNMTJ4RKPVBFQE33JC5FJ"
        }
        r_using = requests.post(url=start_using_url, headers=self.headers, json=data_body_using)
        response_dict_using = json.loads(r_using.text)
        assert response_dict_using.get('msg') == '%s条信息已更新' % len(cassette_ids)

        # 获取载具编号
        sql = "SELECT CARRIER_SN FROM MESAKCOMEDEV.MC_MTM_CARRIER WHERE ID IN ('%s', '%s', '%s', '%s') " % tuple(
            cassette_ids)
        con = ConnectOracle()
        cassette_code = con.connect_oracle(sql)
        # print('cassette_code:', cassette_code)
        return sorted([cassette_code[0][0], cassette_code[1][0], cassette_code[2][0], cassette_code[3][0]])

    def get_cassette(self):
        '''
        获取cassette编号
        :return: list cassette编号 [No1, No2, No3]
        '''
        # 新增cassette
        cassette_url = self.ip_port + '/api/mesbasicakcometest/toolingBackUp/batchSave'
        data_body = {
            "toolingParamList": [
                {
                    "createBy": "afb2463a6bf740dab2aaa5e03d136870",
                    "createDate": "2022-08-24T05:36:58.000+0000",
                    "updateBy": "afb2463a6bf740dab2aaa5e03d136870",
                    "updateDate": "2022-08-24T05:36:58.000+0000",
                    "delFlag": "0",
                    "ctlparamType": "Life",
                    "durationFlag": "N",
                    "usagecntFlag": "Y",
                    "usagecntStd": 999,
                    "usagecntMin": 998,
                    "usagecntMax": 999,
                    "usagecntAlm": 998,
                    "usagecntUnit": "Wafer",
                    "verNo": 0,
                    "ctlparamTypeName": "使用寿命",
                    "usagecntUsed": 999
                },
                {
                    "createBy": "afb2463a6bf740dab2aaa5e03d136870",
                    "createDate": "2022-08-24T05:36:58.000+0000",
                    "updateBy": "afb2463a6bf740dab2aaa5e03d136870",
                    "updateDate": "2022-08-24T05:36:58.000+0000",
                    "delFlag": "0",
                    "ctlparamType": "PM",
                    "durationFlag": "N",
                    "usagecntFlag": "N",
                    "verNo": 0,
                    "ctlparamTypeName": "保养"
                },
                {
                    "createBy": "afb2463a6bf740dab2aaa5e03d136870",
                    "createDate": "2022-08-24T05:36:58.000+0000",
                    "updateBy": "afb2463a6bf740dab2aaa5e03d136870",
                    "updateDate": "2022-08-24T05:36:58.000+0000",
                    "delFlag": "0",
                    "ctlparamType": "Clean",
                    "durationFlag": "N",
                    "usagecntFlag": "N",
                    "verNo": 0,
                    "ctlparamTypeName": "清洗周期"
                }
            ],
            "tooling": {
                "typeName": "花篮类别",
                "toolingKindName": "cassette",
                "toolingQty": 1,
                "singletonFlag": "Y",
                "id": "",
                "delFlag": "0",
                "toolingSn": "",
                "toolingName": "花篮",
                "toolingKind": "Tooling",
                "toolingtypeId": "34b1af2833074a7fbfd0e368f85cc363",
                "toolingcatId": "698b64d650764bf0b8cd6ca7145c07bc",
                "toolingcatCode": "HL",
                "toolingcatName": "花篮",
                "model": "",
                "toolingcatDesc": "HL",
                "toolingState": "Normal",
                "availableFlag": "Y",
                "toolingUom": "2fab2c28b3fa4c0fbe546a8f347c315f",
                "toolingUomname": "片",
                "toolingDesc": "",
                "activeFlag": "I",
                "mtlgroupId": "",
                "mtlgroupNo": "",
                "mtllocId": "",
                "num": "4",
                "snPrefix": "HL",
                "activityDesc": ""
            },
            "toolingAttrList": [],
            "requestId": "SAV8J7TKOI7QA9VV8EAP9S6LST70BEC4"
        }
        r = requests.post(url=cassette_url, headers=self.headers, json=data_body)
        response_dict = json.loads(r.text)
        assert response_dict.get('msg') == '保存成功'
        cassette_ids = response_dict.get('data')
        # print('cassette_ids:', cassette_ids)

        # 启用cassette
        start_using_url = self.ip_port + '/api/mesbasicakcometest/toolingBackUp/updateActiveFlagByIds'
        data_body_using = {
            "activeFlag": "Y",
            "ids": cassette_ids,
            "requestId": "2MGUCBV8VN1HQ3CT10N26OD6LEGMO62N"
        }
        r_using = requests.post(url=start_using_url, headers=self.headers, json=data_body_using)
        response_dict_using = json.loads(r_using.text)
        assert response_dict_using.get('msg') == '%s条信息已更新' % len(cassette_ids)

        # 获取载具编号
        sql = "SELECT TOOLING_SN FROM MESAKCOMEDEV.MC_MTM_TOOLING WHERE ID IN ('%s', '%s', '%s', '%s') " % tuple(
            cassette_ids)
        con = ConnectOracle()
        cassette_code = con.connect_oracle(sql)
        # print('cassette_code:', cassette_code)
        return sorted([cassette_code[0][0], cassette_code[1][0], cassette_code[2][0], cassette_code[3][0]])

    def main(self):
        '''
        主执行
        :return:
        '''
        self.cut_wafer()
        self.decimal_code_result = self.get_whole_wafer()
        self.cassette_code_result = self.get_cassette()


class Mes(Base):
    def __init__(self):
        super().__init__()
        self.mes_ip_port = 'http://192.168.1.155:9084'
        self.whole_decimal_code = None
        self.wo_code = None

    def get_lh_wafer(self):
        '''
        获取料盒wafer十进制码
        :return: int 十进制码
        '''
        lh_wafer_url = self.mes_ip_port + '/cut/wafer/getWaferIdList'
        payload = {
            "eqpCode": "切片机001",
            "carrierSn": "LH01"
        }
        r_lh_wafer = requests.get(url=lh_wafer_url, headers=self.headers, json=payload)
        lh_wafer_response_dict = json.loads(r_lh_wafer.text)
        assert lh_wafer_response_dict.get('msg') == '成功'
        self.whole_decimal_code = lh_wafer_response_dict.get('data')[0].get('waferDecimalCode')
        # print('whole_decimal_code:', self.whole_decimal_code)
        return self.whole_decimal_code

    def cut_wafer_leave(self, eqp_code='切片机001', wo_code='WO202208240001', carrier_sn='HL-s322', qty='2',
                        wafer_list=None):
        '''
        切片出花篮，产出登记，投片
        :param eqp_code: 设备号
        :param wo_code: 工单号
        :param carrier_sn: 载具号
        :param qty: 数量
        :param wafer_list:wafer列表
        :return: 返回响应信息
        '''
        cat_wafer_leave_url = self.mes_ip_port + '/cut/wafer/confirmCut'
        cat_wafer_leave_body = {
            "eqpCode": eqp_code,
            "woCode": wo_code,
            "carrierSn": carrier_sn,
            "qty": qty,
            "waferList": wafer_list
        }
        r = requests.post(url=cat_wafer_leave_url, headers=self.headers, json=cat_wafer_leave_body)
        response_dict = json.loads(r.text)
        print('cut_wafer_leave:', response_dict)
        assert response_dict.get('msg') == '成功'
        return response_dict.get('msg')

    def check_or_out(self, proc_id='CLN', carrier_sn='HL-s551', eqp_code='zrj001', wo_code='WO202208240001',
                     action_view='CheckIn',
                     recipe='test_zr', recipe_ver='3.22', qty='4', wafer_list=None):
        '''

        :param proc_id: 制程号
        :param carrier_sn: 载具号
        :param eqp_code: 设备号
        :param wo_code: 工单
        :param action_view: 上机或下机
        :param recipe: Recipe
        :param recipe_ver: Recipe版本
        :param qty: 数量
        :param wafer_list: wafer列表
        :return: 返回响应信息
        '''
        check_or_out_url = self.mes_ip_port + '/track/checkInOrOut'
        check_or_out_body = {
            "procId": proc_id,
            "carrierSn": carrier_sn,
            "eqpCode": eqp_code,
            "portCode": "01",
            "woCode": wo_code,
            "actionView": action_view,
            "carrierWeight": "1.2345678",
            "recipe": recipe,
            "recipeVer": recipe_ver,
            "qty": qty,
            "waferList": wafer_list
        }
        r = requests.post(url=check_or_out_url, headers=self.headers, json=check_or_out_body)
        response_dict = json.loads(r.text)
        print('check_or_out:', response_dict)
        assert response_dict.get('msg') == '成功'
        return response_dict.get('msg')

    # 到切片
    def to_cut(self):
        pass

    # 到清洗
    def to_cln(self):
        self.cut_wafer_leave(carrier_sn=self.cassette_code_result[0], qty='4',
                             wafer_list=[
                                 {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                                 {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                                 {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                                 {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
                             ])

    # 到CVD
    def to_cvd(self):
        self.cut_wafer_leave(carrier_sn=self.cassette_code_result[0], qty='4',
                             wafer_list=[
                                 {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                                 {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                                 {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                                 {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
                             ])
        # 清洗上下机
        self.check_or_out(proc_id='CLN', carrier_sn=self.cassette_code_result[0], eqp_code='zrj001',
                          action_view='CheckIn', recipe='test_zr', qty='4', wafer_list=[
                {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
            ])
        self.check_or_out(proc_id='CLN', carrier_sn=self.cassette_code_result[0], eqp_code='zrj001',
                          action_view='CheckOut', recipe='test_zr', qty='4', wafer_list=[
                {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
            ])

    # 到PVD
    def to_pvd(self):
        self.cut_wafer_leave(carrier_sn=self.cassette_code_result[0], qty='4',
                             wafer_list=[
                                 {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                                 {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                                 {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                                 {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
                             ])
        # 清洗上下机
        self.check_or_out(proc_id='CLN', carrier_sn=self.cassette_code_result[0], eqp_code='zrj001',
                          action_view='CheckIn', recipe='test_zr', qty='4', wafer_list=[
                {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
            ])
        self.check_or_out(proc_id='CLN', carrier_sn=self.cassette_code_result[0], eqp_code='zrj001',
                          action_view='CheckOut', recipe='test_zr', qty='4', wafer_list=[
                {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
            ])
        # cvd上下机
        self.check_or_out(proc_id='CVD', carrier_sn=self.cassette_code_result[0], eqp_code='PECVD001',
                          action_view='CheckIn', recipe='test_pecvd', qty='4', wafer_list=[
                {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
            ])
        self.check_or_out(proc_id='CVD', carrier_sn=self.cassette_code_result[1], eqp_code='PECVD001',
                          action_view='CheckOut', recipe='test_pecvd', qty='4', wafer_list=[
                {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
            ])

    # 到丝网印刷
    def to_spt(self):
        self.cut_wafer_leave(carrier_sn=self.cassette_code_result[0], qty='4',
                             wafer_list=[
                                 {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                                 {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                                 {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                                 {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
                             ])
        # 清洗上下机
        self.check_or_out(proc_id='CLN', carrier_sn=self.cassette_code_result[0], eqp_code='zrj001',
                          action_view='CheckIn', recipe='test_zr', qty='4', wafer_list=[
                {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
            ])
        self.check_or_out(proc_id='CLN', carrier_sn=self.cassette_code_result[0], eqp_code='zrj001',
                          action_view='CheckOut', recipe='test_zr', qty='4', wafer_list=[
                {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
            ])
        # cvd上下机
        self.check_or_out(proc_id='CVD', carrier_sn=self.cassette_code_result[0], eqp_code='PECVD001',
                          action_view='CheckIn', recipe='test_pecvd', qty='4', wafer_list=[
                {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
            ])
        self.check_or_out(proc_id='CVD', carrier_sn=self.cassette_code_result[1], eqp_code='PECVD001',
                          action_view='CheckOut', recipe='test_pecvd', qty='4', wafer_list=[
                {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
            ])
        # pvd上下机
        self.check_or_out(proc_id='PVD', carrier_sn=self.cassette_code_result[1], eqp_code='PVD001',
                          action_view='CheckIn', recipe='test_pvd', qty='4', wafer_list=[
                {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
            ])
        self.check_or_out(proc_id='PVD', carrier_sn=self.cassette_code_result[2], eqp_code='PVD001',
                          action_view='CheckOut', recipe='test_pvd', qty='4', wafer_list=[
                {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"},
                {"waferDecimalCode": self.decimal_code_result[2], "slot": "2", "waferRow": "1"},
                {"waferDecimalCode": self.decimal_code_result[3], "slot": "2", "waferRow": "2"}
            ])

    def run(self, proc_id):
        # self.main()  # 返回半片十进制码及载具信息
        # print('result:', self.decimal_code_result, self.cassette_code_result)
        # whole_decimal_code = self.get_lh_wafer()
        if proc_id == 'STC':
            self.main()  # 返回半片十进制码及载具信息
            print('result:', self.decimal_code_result, self.cassette_code_result[0])
            whole_decimal_code = self.get_lh_wafer()
            with open('mes_info.txt', 'a+', encoding='utf-8') as file:
                file.write(
                    '%s ---STC--- Wafer: %s  Cassette: %s\n' % (datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                                                                ','.join(
                                                                    [str(wafer) for wafer in self.decimal_code_result]),
                                                                str(self.cassette_code_result[0])))
        elif proc_id == 'CLN':
            self.main()  # 返回半片十进制码及载具信息
            print('result:', self.decimal_code_result, self.cassette_code_result[0])
            whole_decimal_code = self.get_lh_wafer()
            with open('mes_info.txt', 'a+', encoding='utf-8') as file:
                file.write(
                    '%s ---CLN--- Wafer: %s  Cassette: %s\n' % (datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                                                                ','.join(
                                                                    [str(wafer) for wafer in self.decimal_code_result]),
                                                                str(self.cassette_code_result[0])))
                # 调用到cln
            self.to_cln()
        elif proc_id == 'CVD':
            self.main()  # 返回半片十进制码及载具信息
            print('result:', self.decimal_code_result, self.cassette_code_result[0])
            whole_decimal_code = self.get_lh_wafer()
            with open('mes_info.txt', 'a+', encoding='utf-8') as file:
                file.write(
                    '%s ---CVD--- Wafer: %s  Cassette: %s\n' % (datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                                                                ','.join(
                                                                    [str(wafer) for wafer in self.decimal_code_result]),
                                                                str(self.cassette_code_result[0])))
            # 调用到cvd
            self.to_cvd()
        elif proc_id == 'PVD':
            self.main()  # 返回半片十进制码及载具信息
            print('result:', self.decimal_code_result, self.cassette_code_result[1])
            whole_decimal_code = self.get_lh_wafer()
            with open('mes_info.txt', 'a+', encoding='utf-8') as file:
                file.write(
                    '%s ---PVD--- Wafer: %s  Cassette: %s\n' % (datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                                                                ','.join(
                                                                    [str(wafer) for wafer in self.decimal_code_result]),
                                                                str(self.cassette_code_result[1])))
            # 调用到pvd
            self.to_pvd()
        elif proc_id == 'SPT':
            self.main()  # 返回半片十进制码及载具信息
            print('result:', self.decimal_code_result, self.cassette_code_result[2])
            whole_decimal_code = self.get_lh_wafer()
            with open('mes_info.txt', 'a+', encoding='utf-8') as file:
                file.write(
                    '%s ---SPT--- Wafer: %s  Cassette: %s\n' % (datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                                                                ','.join(
                                                                    [str(wafer) for wafer in self.decimal_code_result]),
                                                                str(self.cassette_code_result[2])))
            # 调用到丝网印刷
            self.to_spt()
        else:
            print('请输入：STC、CLN、CVD、PVD、SPT中的制程号')


if __name__ == '__main__':
    # b = Base()
    # b.main()
    # print('result:', b.decimal_code_result, b.cassette_code_result)
    for _ in range(1):
        m = Mes()
        # 请输入：STC、CLN、CVD、PVD、SPT中的制程号
        m.run(proc_id='CLN')
