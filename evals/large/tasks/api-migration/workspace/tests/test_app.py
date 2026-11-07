import unittest

from tests.fake import FakeTransport

from app import health, poller, weather


class WeatherTests(unittest.TestCase):
    def test_reads_value_with_two_second_timeout(self):
        with FakeTransport() as fake:
            url = "https://weather.example.com/now?city=Oslo"
            self.assertEqual(weather.current_temp("Oslo"), len(url))
        self.assertEqual(fake.calls, [("GET", url, 2.0)])


class HealthTests(unittest.TestCase):
    def test_ok(self):
        with FakeTransport([200]) as fake:
            self.assertEqual(health.check("https://svc.example.com/h"), "ok")
        self.assertEqual(len(fake.calls), 1)
        self.assertAlmostEqual(fake.calls[0][2], 0.25)

    def test_down_on_transport_failure_single_attempt(self):
        with FakeTransport(["fail", "fail"]) as fake:
            self.assertEqual(health.check("https://svc.example.com/h"), "down")
        self.assertEqual(len(fake.calls), 1)

    def test_down_on_http_error(self):
        with FakeTransport([503]):
            self.assertEqual(health.check("https://svc.example.com/h"), "down")


class PollerTests(unittest.TestCase):
    def test_retries_then_succeeds(self):
        with FakeTransport(["fail", "fail", 200]) as fake:
            p = poller.Poller("https://svc.example.com/p", timeout_ms=1500, retries=2)
            self.assertTrue(p.poll().startswith("up:"))
        self.assertEqual([c[2] for c in fake.calls], [1.5, 1.5, 1.5])

    def test_gives_up_after_retries(self):
        with FakeTransport(["fail"] * 5) as fake:
            p = poller.Poller("https://svc.example.com/p", timeout_ms=1500, retries=2)
            self.assertEqual(p.poll(), "down:None")
        self.assertEqual(len(fake.calls), 3)


if __name__ == "__main__":
    unittest.main()
