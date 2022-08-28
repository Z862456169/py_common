import locust
import random


class Test(locust.SequentialTaskSet):
    """会按顺序执行，task中的数字表示执行的次数而非权重"""

    @locust.task(1)
    def test_step1(self):
        print("step1")
        self.data = random.randint(1, 6)
        print("step1_data: ", self.data)

    @locust.task(1)
    def test_step2(self):
        print("step2")
        print("step2_data: ", self.data)


class MyUser(locust.HttpUser):
    tasks = [Test]
    wait_time = locust.between(1, 2)
    # host = ''
