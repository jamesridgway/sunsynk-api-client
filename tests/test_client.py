from sunsynk.client import SunsynkClient
from tests.test_utils import sunsynk_vcr

vcr = sunsynk_vcr()

class TestClient:
    def test_login(self):
        with vcr.use_cassette('tests/cassettes/test_client/login.yaml'):
            assert SunsynkClient('user@example.com', 'letmein')

    def test_get_inverters(self):
        with vcr.use_cassette('tests/cassettes/test_client/get_inverters.yaml'):
            client = SunsynkClient('user@example.com', 'letmein')
            inverters = client.get_inverters()
            assert inverters[0].sn == '1234567890'

