import yaml

from smz.made_data.wlh_bak.connect_oracle.connect_oracle import ConnectOracle
from smz.made_data.wlh_bak.op_chrome.get_si_data import OpChrome


def get_yaml():
    with open('data.yml', 'r', encoding='utf-8') as file:
        result = yaml.safe_load(file)
    print(result[0])
    print(type(result))

    # file = open('./data.yml', 'r', encoding='utf-8')
    # result = file.read()
    # file.close()
    # x = yaml.load(result,Loader=yaml.FullLoader)
    # print(x)
    # print(type(x))


def main():
    url_login = 'http://192.168.1.127:9995/USERCENTER/gateway2'
    url_cut = 'http://192.168.1.127:9997/AKCOMEMES/waferSlicingModule/waferSlicingIndexModule'
    username = 'WLH001'
    password = '123456'
    woCode = 'WO202202280001'
    si_code = 'Y-1.220304.001'
    opc = OpChrome(url_login, url_cut, username, password, woCode, si_code)
    wafer_whole = opc.run()
    print("wafer_whole:", wafer_whole)

    sql = "SELECT ENTIRE_DECIMAL_CODE FROM MESAKCOMEDEV.MC_BASE_WAFER_INFO WHERE PARENT_ID IN (SELECT ID FROM MESAKCOMEDEV.MC_BASE_WAFER_INFO WHERE WAFER_NO IN ('{}'))".format(
        wafer_whole)
    con = ConnectOracle()
    half_wafer = con.connect_oracle(sql)
    print("half_wafer:", half_wafer)


if __name__ == '__main__':
    main()
