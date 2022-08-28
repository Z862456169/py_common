import locust


class Test(locust.TaskSet):
    """task中的数字表示执行的权重"""

    @locust.task(1)
    def test_step1(self):
        print("step1")

    @locust.task(3)
    def test_step3(self):
        print("step3")
        print(self.user.smz)

    @locust.task(1)
    def test_step2(self):
        print("step2")


class MyUser(locust.HttpUser):
    tasks = [Test]
    wait_time = locust.between(1, 2)
    smz = 666
    # host = ''
