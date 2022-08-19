import requests
import json
from smz.made_data.wlh_bak.base_bak.getticket import get_ticket
import urllib.parse
from smz.made_data.wlh_bak.base_bak.connect_oracle import ConnectOracle
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
            "woId": "HEE1UTD54LK57D3DDU6M7B4J6BQAIRGQ",
            "woCode": "WO202202280001",
            "waferCode": "Y-1",
            "waferSpec": "210硅片",
            "siliconWaferLotNo": "",
            "eqpCode": "切片机001", "carrierSn": "LH01",
            "totalQty": "1",
            "waferSizeName": "对角线:200mm边长:156*156mm",
            "waferId": "449703427eed4e8598ca8f14e869142a",
            "siliconWaferLotList": ["Y-1.220304.001"],
            "requestId": "URBSV2L6T4LM7SJBVLS7CDBGSD973P41"
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
        cut_url_byte = urllib.parse.quote(cut_url_value)
        cut_url = self.ip_port + '/api/mesakcometest/cut/wafer/manage/findList?' + cut_url_byte
        response_dict = json.loads(requests.get(url=cut_url).text)  # 转字典
        wafer_id = response_dict.get('rows')[0].get('id')
        # print('cutWaferManageId:', wafer_id)

        # 获取整片长码
        whole_url_value = '{"cutWaferManageId": "%s", "cutFlag": "N", "type": "Whole","status": "Normal","outputFlag": "", "pageNo": 1, "pageSize": 15, "requestId": "OKHML0I8C13IF73PBJ4E2OL5M7C54J9S"}' % wafer_id
        whole_url_byte = urllib.parse.quote(whole_url_value)
        whole_url = self.ip_port + '/api/mesakcometest/cut/wafer/manage/findWaferList?' + whole_url_byte
        whole_response_dict = json.loads(requests.get(url=whole_url).text)  # 转字典
        whole_wafer_no = whole_response_dict.get('rows')[0].get('waferNo')
        # print('whole_wafer_no:', whole_wafer_no)

        # 操作数据库获取整片十进制码
        sql = "SELECT ENTIRE_DECIMAL_CODE FROM MESAKCOMEDEV.MC_BASE_WAFER_INFO WHERE PARENT_ID IN (SELECT ID FROM MESAKCOMEDEV.MC_BASE_WAFER_INFO WHERE WAFER_NO IN ('%s'))" % whole_wafer_no
        con = ConnectOracle()
        decimal_code = con.connect_oracle(sql)
        print('get_whole_wafer:', decimal_code)
        return [decimal_code[0][0], decimal_code[1][0]]

    def get_cassette(self):
        '''
        获取cassette编号
        :return: list cassette编号 [No1, No2, No3]
        '''
        # 新增cassette
        cassette_url = self.ip_port + '/api/mesbasicakcometest/carrier/addCarrier'
        data_body = {
            "carrierKind": "FB",
            "startCode": "1",
            "inputCount": "3",
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
        sql = "SELECT CARRIER_SN FROM MESAKCOMEDEV.MC_MTM_CARRIER WHERE ID IN ('%s', '%s', '%s') " % tuple(cassette_ids)
        con = ConnectOracle()
        cassette_code = con.connect_oracle(sql)
        print('cassette_code:', cassette_code)
        return [cassette_code[0][0], cassette_code[1][0], cassette_code[2][0]]

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
        print('whole_decimal_code:', self.whole_decimal_code)
        return self.whole_decimal_code

    def cut_wafer_check_aoi(self, proc_id='STC', eqp_code='切片机001', whole_decimal_code=None):
        '''
        切片aoi检测
        :param proc_id: 制程号
        :param eqp_code: 设备号
        :param whole_decimal_code: 整片十进制码
        :return: 检测返回信息
        '''
        cut_check_aoi_url = self.mes_ip_port + '/cut/wafer/checkForAOI'
        cut_check_aoi_body = {
            "procId": proc_id,
            "eqpCode": eqp_code,
            "waferDecimalCode": whole_decimal_code,
            "portCode": "1",
            "measurerId": "SMZtest",
            "direction": "1",
            "rank": "A",
            "defectCode": "Q02",
            "fileUrl": "http://www.baidu.com",
            "time": "20220311213010"
        }
        r = requests.post(url=cut_check_aoi_url, headers=self.headers, json=cut_check_aoi_body)
        response_dict = json.loads(r.text)
        print('cut_wafer_check_aoi:', response_dict)
        assert response_dict.get('msg') == '成功'
        return response_dict.get('msg')

    def cut_wafer_info(self, proc_id='STC', eqp_code='切片机001', whole_decimal_code=None, type='in'):
        '''
        wafer信息登记
        :param proc_id: 制程号
        :param eqp_code: 设备号
        :param whole_decimal_code: 整片十进制码
        :param type: 进设备或出设备
        :return: 响应信息
        '''
        cut_wafer_info_url = self.mes_ip_port + '/cut/wafer/info'
        cut_wafer_info_body = {
            "procId": proc_id,
            "eqpCode": eqp_code,
            "waferDecimalCode": whole_decimal_code,
            "chamberCode": "01",
            "type": type
        }
        r = requests.post(url=cut_wafer_info_url, headers=self.headers, json=cut_wafer_info_body)
        response_dict = json.loads(r.text)
        print('cut_wafer_info:', response_dict)
        assert response_dict.get('msg') == '成功'
        return response_dict.get('msg')

    def cassette_leave(self, carrier_sn=None):
        cassette_leave_url = self.mes_ip_port + '/track/cassette/release'
        cassette_leave_body = {
            "carrierSn": carrier_sn
        }
        r = requests.post(url=cassette_leave_url, headers=self.headers, json=cassette_leave_body)
        response_dict = json.loads(r.text)
        print('cassette_leave:', response_dict)
        assert response_dict.get('msg') == '成功'
        return response_dict.get('msg')

    def carrier_info_register(self, proc_id='CVD', carrier_sn='TP012', eqp_code='PECVD001', action='in',
                              tray_position='upper'):
        '''
        载具信息登记
        :param proc_id: 制程号
        :param carrier_sn: 载具号
        :param eqp_code: 设备号
        :param action: 进设备或出设备
        :param tray_position: 载具位置
        :return: 返回响应信息
        '''
        carrier_info_register_url = self.mes_ip_port + '/info/carrier'
        carrier_info_register_body = {
            "procId": proc_id,
            "carrierSn": carrier_sn,
            "eqpCode": eqp_code,
            "chamberCode": "01",
            "action": action,
            "trayPosition": tray_position
        }
        r = requests.post(url=carrier_info_register_url, headers=self.headers, json=carrier_info_register_body)
        response_dict = json.loads(r.text)
        print('carrier_info_register:', response_dict)
        assert response_dict.get('msg') == '成功'
        return response_dict.get('msg')

    def wafer_defect_register(self, proc_id='STC', eqp_code='切片机001', wafer_decimal_code=None):
        '''
        wafer踢片碎片登记
        :param proc_id: 制程号
        :param eqp_code: 设备号
        :param wafer_decimal_code: wafer十进制码
        :return: 返回响应信息
        '''
        wafer_defect_register_url = self.mes_ip_port + '/cut/wafer/defect'
        wafer_defect_register_body = {
            "procId": proc_id,
            "eqpCode": eqp_code,
            "chamberCode": "槽体001",
            "waferDecimalCode": wafer_decimal_code,
            "defectCode": "C44",
            "type": "Remove"
        }
        r = requests.post(url=wafer_defect_register_url, headers=self.headers, json=wafer_defect_register_body)
        response_dict = json.loads(r.text)
        print('wafer_defect_register:', response_dict)
        assert response_dict.get('msg') == '成功'
        return response_dict.get('msg')

    def dry_in_or_out(self, proc_id='SPT', carrier_sn='HL-s195', eqp_code='swys001', action='in', qty=1,
                      wafer_list=None):
        '''
        烘干设备cassette进出
        :param proc_id: 制程号
        :param carrier_sn: 载具号
        :param eqp_code: 设备号
        :param action: 进或出
        :param qty: 数量
        :param wafer_list:wafer列表
        :return: 返回响应信息
        '''
        dry_in_or_out_url = self.mes_ip_port + '/info/dry/InOrOut'
        dry_in_or_out_body = {
            "procId": proc_id,
            "carrierSn": carrier_sn,
            "eqpCode": eqp_code,
            "chamberCode": "11",
            "action": action,
            "qty": qty,
            "waferList": wafer_list
        }
        r = requests.post(url=dry_in_or_out_url, headers=self.headers, json=dry_in_or_out_body)
        response_dict = json.loads(r.text)
        print('dry_in_or_out:', response_dict)
        assert response_dict['msg'] == '成功'
        return response_dict['msg']

    def battery_weight(self, proc_id='SPT', eqp_code='swys001', print_code='A', wafer_decimal_code=None, weight='3.22',
                       type='before'):
        '''
        电池片进出
        :param proc_id:制程号
        :param eqp_code: 设备号
        :param print_code: 印台号
        :param wafer_decimal_code:wafer十进制码
        :param weight: 重量
        :param type: 称重前或后
        :return:
        '''
        batter_weight_url = self.mes_ip_port + '/info/battery/weight'
        batter_weight_body = {
            "procId": proc_id,
            "eqpCode": eqp_code,
            "printCode": print_code,
            "waferDecimalCode": wafer_decimal_code,
            "weight": weight,
            "type": type
        }
        r = requests.post(url=batter_weight_url, headers=self.headers, json=batter_weight_body)
        response_dict = json.loads(r.text)
        print('battery_weight:', response_dict)
        assert response_dict.get('msg') == '成功'
        return response_dict.get('msg')

    def battery_print_eqp_in_or_out(self, proc_id='SPT', eqp_code='swys001', print_code='A', wafer_decimal_code=None,
                                    action='in'):
        '''
        电池片进出印刷设备
        :param proc_id: 制程号
        :param eqp_code: 设备号
        :param print_code: 印台号：A、B、C、D
        :param wafer_decimal_code: wafer十进制码
        :param action: 进出设备
        :return: 返回响应信息
        '''
        battery_print_eqp_url = self.mes_ip_port + '/info/battery/print'
        battery_print_eqp_body = {
            "procId": proc_id,
            "eqpCode": eqp_code,
            "printCode": print_code,
            "waferDecimalCode": wafer_decimal_code,
            "action": action,
            "time": str(datetime.datetime.now().strftime('%Y%m%d%H%M'))
        }
        r = requests.post(url=battery_print_eqp_url, headers=self.headers, json=battery_print_eqp_body)
        response_dict = json.loads(r.text)
        print('battery_print_eqp_in_or_out:', response_dict)
        assert response_dict.get('msg') == '成功'
        return response_dict.get('msg')

    def eqp_status(self, eqp_code='zrj001', status='PRD'):
        '''
        设备状态变更上报
        :param eqp_code:设备号
        :param status: 状态
        :return: 返回响应信息
        '''
        eqp_status_url = self.mes_ip_port + '/track/eqp/status'
        eqp_status_body = {
            "eqpCode": eqp_code,
            "status": status
        }
        r = requests.post(url=eqp_status_url, headers=self.headers, json=eqp_status_body)
        response_dict = json.loads(r.text)
        print('eqp_status:', response_dict)
        assert response_dict.get('msg') == '成功'
        return response_dict.get('msg')

    def tray_wafer_register(self, proc_id='PVD', eqp_code='PVD001', carrier_sn='HL-s213', tray_position='upper',
                            wafer_list=None):
        '''
        托盘wafer登记（累加使用次数）
        :param proc_id: 制程号
        :param eqp_code: 设备号
        :param carrier_sn: 载具号
        :param tray_position: 托盘位置
        :param wafer_list: wafer列表：[{
                                            "waferDecimalCode": "4095737955",
                                            "slot": "1",
                                            "waferRow": "1"
                                        },
                                        {
                                            "waferDecimalCode": "4095737956",
                                            "slot": "1",
                                            "waferRow": "2"
                                        }]
        :return:返回响应信息
        '''
        tray_wafer_register_url = self.mes_ip_port + '/info/tray/wafer'
        tray_wafer_register_body = {
            "procId": proc_id,
            "eqpCode": eqp_code,
            "carrierSn": carrier_sn,
            "trayPosition": tray_position,
            "waferList": wafer_list
        }
        r = requests.post(url=tray_wafer_register_url, headers=self.headers, json=tray_wafer_register_body)
        response_dict = json.loads(r.text)
        print('tray_wafer_register:', response_dict)
        assert response_dict.get('success') is True
        return response_dict.get('msg')

    def tray_maintenance(self, proc_id='PVD', carrier_sn='HL-s213', eqp_code='PVD001', type='Coating',
                         action_type='End', location='upper'):
        '''
        托盘维保
        :param proc_id: 制程号
        :param carrier_sn: 载具号
        :param eqp_code: 设备号
        :param type: 重置清洗或镀膜
        :param action_type: 重置节点
        :param location: 上行或下行
        :return: 返回响应信息
        '''
        tray_maintenance_url = self.mes_ip_port + '/info/tray/maintenance'
        # int(datetime.datetime.now().timestamp())*1000  转成ms时间戳给后台
        tray_maintenance_body = {
            "procId": proc_id,
            "carrierSn": carrier_sn,
            "eqpCode": eqp_code,
            "chamberCode": "01",
            "type": type,
            "actionTime": int(datetime.datetime.now().timestamp()) * 1000,
            "actionType": action_type,
            "location": location
        }
        r = requests.post(url=tray_maintenance_url, headers=self.headers, json=tray_maintenance_body)
        response_dict = json.loads(r.text)
        print('tray_maintenance:', response_dict)
        assert response_dict.get('msg') == '成功'
        return response_dict.get('msg')

    def cut_wafer_leave(self, eqp_code='切片机001', wo_code='WO202202280001', carrier_sn='HL-s322', qty='2',
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

    def bin_out(self):
        pass

    def carrier_weight(self):
        pass

    def track_in_or_out(self):
        pass

    def pl_check(self):
        pass

    def aoi_check(self):
        pass

    def el_check(self):
        pass

    def iv_check(self):
        pass

    def sr_check(self):
        pass

    def run(self):
        self.main()  # 返回半片十进制码及载具信息
        print('result:', self.decimal_code_result, sorted(self.cassette_code_result))
        whole_decimal_code = self.get_lh_wafer()
        self.cut_wafer_check_aoi(whole_decimal_code=539492354)  # whole_decimal_code 要传递
        self.cut_wafer_info(whole_decimal_code='539492354')
        self.cassette_leave(carrier_sn='HL-s260')
        self.carrier_info_register()
        self.wafer_defect_register(wafer_decimal_code=539492354)  # whole_decimal_code 要传递
        self.dry_in_or_out(wafer_list=[{"waferDecimalCode": "4095737947", "slot": "1", "waferRow": "1"}])
        self.battery_weight(wafer_decimal_code="4095737948")
        self.battery_print_eqp_in_or_out(wafer_decimal_code='4095737951')
        self.eqp_status()
        self.tray_wafer_register(wafer_list=[{"waferDecimalCode": "4095737955", "slot": "1", "waferRow": "1"},
                                             {"waferDecimalCode": "4095737956", "slot": "1", "waferRow": "2"}])
        self.tray_maintenance()
        # self.cut_wafer_leave(carrier_sn=self.cassette_code_result[0], wafer_list=[
        #     {"waferDecimalCode": self.decimal_code_result[0], "slot": "1", "waferRow": "1"},
        #     {"waferDecimalCode": self.decimal_code_result[1], "slot": "1", "waferRow": "2"}])


if __name__ == '__main__':
    b = Base()
    b.main()
    print('result:', b.decimal_code_result, sorted(b.cassette_code_result))
    # m = Mes()
    # m.run()
