import logging
from datetime import datetime
import os
import platform


def get_log():
    now_date = datetime.now().strftime('%Y%m%d')
    # 当前文件上一级目录
    dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if platform.system().lower() == 'windows':
        logs_path = dir_path + "\\logs\\"
    elif platform.system().lower() == 'linux':
        logs_path = dir_path + '/logs/'
    if os.path.exists(logs_path) is not True:
        os.mkdir(logs_path)
    log_file_path = logs_path + now_date + '.log'
    print('log_file_path:', log_file_path)

    # 1、创建日志器、设置全局日志等级
    logger = logging.getLogger('smz')
    logger.setLevel(logging.DEBUG)

    # 输出格式定义
    file_fmt = '%(asctime)s %(name)s %(levelname)s %(funcName)s:%(lineno)d:%(message)s'
    file_formatter = logging.Formatter(file_fmt)
    console_fmt = '%(asctime)s-%(name)s-%(levelname)s-%(funcName)s:%(lineno)d:%(message)s'
    console_formatter = logging.Formatter(console_fmt)

    # 2、设置输出日志到文件、设置输出到文件的日志级别、格式
    file_handle = logging.FileHandler(filename=log_file_path, encoding='utf-8', mode='a')
    file_handle.setLevel(logging.ERROR)
    file_handle.setFormatter(file_formatter)
    # 添加处理器到日志器中
    logger.addHandler(file_handle)

    # 3、设置输出日志到控制台、设置输出到控制台的日志级别、格式
    console_handle = logging.StreamHandler()
    console_handle.setLevel(logging.INFO)
    console_handle.setFormatter(console_formatter)
    # 添加处理器到日志器中
    logger.addHandler(console_handle)

    # 4、调用logger 如：logger.error('error test')
    return logger


if __name__ == '__main__':
    # log_demo()
    logger = get_log()
    logger.error('error test')
