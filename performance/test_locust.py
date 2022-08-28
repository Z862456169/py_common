import locust


class MyUser(locust.HttpUser):
    wait_time = locust.between(1, 2)

    @locust.task
    def test_baidu(self):
        resp = self.client.get("https://www.baidu.com")
        status_code = resp.status_code
        assert 200 == status_code
