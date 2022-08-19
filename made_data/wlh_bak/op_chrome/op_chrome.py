from selenium import webdriver
from selenium.webdriver.common.by import By
import time


class OpChrome:
    def __init__(self, url, user_name, password):
        self.url = url
        self.driver = webdriver.Chrome()
        self.user_name = user_name
        self.password = password
        self.driver.get(self.url)
        self.driver.maximize_window()

    def login(self):
        # 页面登录
        self.driver.find_element(by=By.XPATH,
                                 value='//*[@id="layout"]/div[2]/div/div/div[2]/form/div[1]/div/div/input').send_keys(
            self.user_name)
        self.driver.find_element(by=By.XPATH,
                                 value='//*[@id="layout"]/div[2]/div/div/div[2]/form/div[2]/div/div/input').send_keys(
            self.password)

        self.driver.find_element(by=By.XPATH,
                                 value='//*[@id="layout"]/div[2]/div/div/div[3]/span/button[1]').click()

    def op_run(self):
        try:
            time.sleep(1)
            self.driver.find_element(by=By.XPATH,
                                     value='//*[@id="mainContent"]/div/div[1]/div[1]/div[2]/div/div[3]/table/tbody/tr[1]').click()
            # self.driver.find_element(by=By.CLASS_NAME,
            #                          value='el-table__row xh-highlight').click()
            time.sleep(1)
            self.driver.find_element(by=By.XPATH,
                                     value='//*[@id="mainContent"]/div/div[1]/div[2]/div[2]/button[2]').click()
            time.sleep(1)
            self.driver.find_element(by=By.XPATH, value='/html/body/div[3]/div/div[3]/button[2]').click()
            time.sleep(1)
        except Exception as error:
            print("error:", error)

    def final(self):
        self.driver.quit()


if __name__ == '__main__':
    url = 'http://192.168.1.127:9997/AKCOMEMESOP/lotGoodsModule/lotGoodsListMoudle?eqpId=a26bcf7ad36e4dc2baaa826a9e04d1e0&eqpCode=zrj001&canUse=Y'
    url2 = 'http://192.168.1.127:9997/AKCOMEMESOP/lotGoodsModule/lotGoodsListMoudle?eqpId=0b2a252f8fef4c1596fd50fdb0500790&eqpCode=PECVD001&canUse=Y'
    url3 = 'http://192.168.1.127:9997/AKCOMEMESOP/lotGoodsModule/lotGoodsListMoudle?eqpId=3e15ccf0e83d4e7e960e645116968608&eqpCode=PVD001&canUse=Y'
    username = 'WLH001'
    password = '123456'
    opc = OpChrome(url3, username, password)
    opc.login()
    for i in range(5):
        opc.op_run()
    opc.final()
