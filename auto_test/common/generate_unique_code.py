import datetime


class GenerateUniqueCode(object):
    def __init__(self, pre_flag=''):
        self.pre_flag = pre_flag

    def unicode_func(self):
        num = 0

        def inner():
            nonlocal num
            num += 1
            return self.pre_flag + str(num)

        return inner

    def time_unicode_func(self):
        num, previous_time = 0, ''

        def inner():
            nonlocal num, previous_time  # nonlocal：声明外部变量
            current_time = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))[2:]  # 格式化当前时间
            if previous_time != current_time:
                num = 0
            num, previous_time = num + 1, current_time
            return self.pre_flag + str(current_time) + '%06d' % num

        return inner


if __name__ == '__main__':
    # 调用时若给前缀标识则拼接生成前缀标识+时间戳+六位流水码；若无前缀标识则拼接生成时间戳+六位流水码
    g = GenerateUniqueCode('stest')
    ge = g.time_unicode_func()
    for _ in range(10 ** 1):
        print(ge())
