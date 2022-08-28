import locust
import random


class Test(locust.TaskSet):
    """task中的数字表示执行的权重"""

    data = random.randint(1, 6)

    # 客户端启动之前需要执行的步骤，只会执行一次
    def on_start(self):
        res = random.randint(1, 6)
        self.res = res

    @locust.task(1)
    def test_step1(self):
        print('on star data：', self.res)
        print('data：', self.data)


class MyUser(locust.HttpUser):
    tasks = [Test]
    wait_time = locust.between(1, 2)
    # host = ''
