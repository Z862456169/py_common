import locust
import queue


def get_data():
    # 创建队列maxsize=0不限制队列大小
    que = queue.Queue(maxsize=0)
    for i in range(1, 6):
        # 往队列里塞入值，队列满了则抛queue.Full异常
        que.put_nowait(i)
        print("que_size: ", que.qsize())
    return que


class Test(locust.TaskSet):
    """task中的数字表示执行的权重"""

    @locust.task(1)
    def test_step1(self):
        # self.user调用MyUser类中的属性
        # get_nowait()从队列中取值，队列空了会抛出queue.Empty异常
        data = self.user.queue_data.get_nowait()
        print(data)
        self.user.queue_data.put_nowait(data)  # 取出的值重新塞入


class MyUser(locust.HttpUser):
    tasks = [Test]
    wait_time = locust.between(1, 2)
    queue_data = get_data()
    # host = ''
