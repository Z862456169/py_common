import locust


class Test(locust.SequentialTaskSet):
    """会按顺序执行，task中的数字表示执行的次数而非权重"""
    @locust.task(1)
    def test_step1(self):
        print("step1")

    @locust.task(1)
    def test_step3(self):
        print("step3")

    @locust.task(1)
    def test_step2(self):
        print("step2")


class MyUser(locust.HttpUser):
    tasks = [Test]
    wait_time = locust.between(1, 2)
    # host = ''
