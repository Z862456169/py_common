from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time


class OpChrome:
    def __init__(self, url_login, url_cut, user_name, password, woCode, si_code):
        self.url = url_login
        self.url_cut = url_cut
        self.user_name = user_name
        self.password = password
        self.woCode = woCode
        self.si_code = si_code
        # 启动chrome
        self.driver = webdriver.Chrome(executable_path='D:\pyfiles\wlh\op_chrome\chromedriver.exe')
        self.driver.get(self.url)
        self.driver.maximize_window()

    def login(self):
        # 页面登录
        self.driver.find_element(by=By.XPATH,
                                 value='/html/body/div/div[1]/div/div[2]/form/div[1]/div/div/div[1]/input').send_keys(
            self.user_name)
        self.driver.find_element(by=By.XPATH,
                                 value='/html/body/div/div[1]/div/div[2]/form/div[2]/div/div/div/input').send_keys(
            self.password)

        self.driver.find_element(by=By.XPATH,
                                 value='/html/body/div/div[1]/div/div[2]/div/div').click()

    def click_to_cut_manage(self, w_time):
        '''
        入到切片管理页面
        :param w_time:
        :return:
        '''
        # 获取整片
        time.sleep(w_time)
        self.driver.find_element(by=By.XPATH,
                                 value='/html/body/div/div[2]/div/div/div/div/div/div[1]/div/div').click()  # 点击爱康MES
        time.sleep(w_time)
        current_windows = self.driver.window_handles  # 获得句柄
        time.sleep(w_time)
        self.driver.switch_to.window(current_windows[-1])  # 窗口切换
        js = 'window.open("{}");'.format(self.url_cut)
        self.driver.execute_script(js)
        time.sleep(w_time)
        current_windows = self.driver.window_handles  # 获得句柄
        time.sleep(1)
        self.driver.switch_to.window(current_windows[-1])  # 窗口切换
        time.sleep(w_time)
        # 点击工单管理
        self.driver.find_element(by=By.XPATH,
                                 value='//*[@id="layout"]/div[1]/div[2]/div[1]/div/ul/div[6]/li/div/span').click()
        time.sleep(w_time)
        # 点击切片管理
        self.driver.find_element(by=By.XPATH,
                                 value='//*[@id="layout"]/div[1]/div[2]/div[1]/div/ul/div[6]/li/ul/div[3]/li').click()
        time.sleep(w_time)

    def cut_manage(self, w_time):
        '''
        操作切片管理获得整片信息
        :param w_time:
        :return:返回整片数据
        '''
        # 点击切片登记
        self.driver.find_element(by=By.XPATH, value='//span[text()="切片登记"][1]').click()
        time.sleep(w_time)
        # 点击工单按钮
        self.driver.find_element(by=By.XPATH, value='//form/div[1]/div/div/div/button').click()
        time.sleep(w_time)
        self.driver.find_element(by=By.XPATH,
                                 value="//div[contains(text(),'{}')]".format(self.woCode)).click()  # 点击工单号
        time.sleep(w_time)
        # 点击确定
        self.driver.find_element(by=By.XPATH,
                                 value='//*[@id="mainContent"]/div/div[3]/div[2]/div/div[3]/span/div/button[1]').click()
        time.sleep(w_time)
        # 键入来料批号、机台号、料盒id、数量
        self.driver.find_element(by=By.XPATH,
                                 value='//form/div[4]/div[1]/div[1]/div/div/input').send_keys(self.si_code)
        self.driver.find_element(by=By.XPATH,
                                 value='//form/div[4]/div[1]/div[1]/div/div/input').send_keys(Keys.ENTER)
        time.sleep(w_time)
        self.driver.find_element(by=By.XPATH, value='//div/div[2]/div/div/input').send_keys("切片机001")
        time.sleep(w_time)
        self.driver.find_element(by=By.XPATH, value='//div/div[3]/div/div/input').send_keys("LH01")
        time.sleep(w_time)
        self.driver.find_element(by=By.XPATH, value='//div/div[4]/div/div/input').send_keys("1")
        time.sleep(w_time)
        # 点击确定
        self.driver.find_element(by=By.XPATH,
                                 value='//*[@id="mainContent"]/div[1]/div[3]/div/div/div[3]/span/div/button[2]/span').click()
        time.sleep(w_time)

        # 获取wafer信息
        self.driver.find_element(by=By.XPATH, value='//table/tbody/tr[1]/td[8]/div/button/span').click()
        self.driver.switch_to.default_content()  # 出弹框后返回到顶层窗口
        time.sleep(w_time)
        whole_wafer = self.driver.find_element(by=By.XPATH,
                                               value='/html/body/div[3]/div/div[2]/div[2]/div[3]/table/tbody/tr/td[3]/div').text
        return whole_wafer

    def final(self):
        self.driver.quit()

    def run(self):
        try:
            self.login()
            self.click_to_cut_manage(w_time=2)
            whole_wafer = self.cut_manage(w_time=2)
        finally:
            self.final()
        return whole_wafer


if __name__ == '__main__':
    url_login = 'http://192.168.1.127:9995/USERCENTER/gateway2'
    url_cut = 'http://192.168.1.127:9997/AKCOMEMES/waferSlicingModule/waferSlicingIndexModule'
    username = 'WLH001'
    password = '123456'
    woCode = 'WO202202280001'
    si_code = 'Y-1.220304.001'
    opc = OpChrome(url_login, url_cut, username, password, woCode, si_code)
    wafer_whole = opc.run()
    print("wafer_whole:", wafer_whole)
