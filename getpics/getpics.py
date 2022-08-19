import requests
import time
from selenium import webdriver
import os


def get_pics(search_word):
    # 图片url
    list_pics = []
    driver = webdriver.Chrome()
    # 控制浏览器访问url地址
    driver.get("https://image.baidu.com/")
    # 搜索目标图片
    driver.find_element_by_id('kw').send_keys(search_word)
    driver.find_element_by_xpath('//*[@id="homeSearchForm"]/span[2]/input').click()
    # 执行js代码滚动页面
    js = 'window.scrollTo(0,5000)'
    for i in range(500):
        driver.execute_script(js)
        # time.sleep(0.01)
    # 获取单张图片url
    for j in range(1, 6):
        for i in range(1, 21):
            try:
                element = driver.find_element_by_xpath('//*[@id="imgid"]/div[%s]/ul/li[%s]/div/a/img' % (j, i))
                ele_pic = element.get_attribute('data-imgurl')
                list_pics.append(ele_pic)
            except:
                print("%s，有广告占用页面，快跑，跳过它，狗砸！" % search_word)
                element = driver.find_element_by_xpath('//*[@id="imgid"]/div[%s]/ul/li[%s]/div/a/img' % (j + 1, i + 2))
                ele_pic = element.get_attribute('data-imgurl')
                list_pics.append(ele_pic)

    # time.sleep(0.1)
    # 退出浏览器
    driver.quit()

    print('%s图片url:' % search_word, list_pics)
    print('%s图片url个数:' % search_word, len(list_pics))
    # 创建文件夹
    os.mkdir(search_word)
    # 保存图片
    for i, url in enumerate(list_pics):
        response = requests.get(url).content  # 二进制文件
        pic_save_url = './' + search_word + '/' + search_word + '_' + str(i + 1) + '.jpg'
        with open(pic_save_url, 'wb') as file:
            file.write(response)


if __name__ == '__main__':
    start_time = time.time()
    search_words = ['雨伞']
    # 单个执行
    # search_word = '钢铁侠'
    # get_pics(search_word)
    # 多个执行
    for search_word in search_words:
        get_pics(search_word)

    end_time = time.time()
    cost_time = end_time - start_time
    print('共计花费%.2f秒' % cost_time)

