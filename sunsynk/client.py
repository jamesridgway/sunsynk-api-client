import requests

from sunsynk.battery import Battery
from sunsynk.plant import Plant


class SunsynkClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.__login()

    def get_plants(self):
        plants =  self.__get('api/v1/plants?page=1&limit=10&name=&status=').json()['data']['infos']
        return [Plant(data) for data in plants]

    def get_inverters(self):
        return self.__get('api/v1/inverters?page=1&limit=10&total=0&status=-1&sn=&plantId=&type=-2&softVer=&'\
                          'hmiVer=&agentCompanyId=-1&gsn=')

    def get_inverter_realtime_input(self, inverter_sn):
        return self.__get(f'api/v1/inverter/{inverter_sn}/realtime/input')

    def get_inverter_realtime_output(self, inverter_sn):
        return self.__get(f'api/v1/inverter/{inverter_sn}/realtime/output')

    def get_inverter_realtime_grid(self, inverter_sn):
        return self.__get(f'api/v1/inverter/grid/{inverter_sn}/realtime?sn={inverter_sn}')

    def get_inverter_realtime_battery(self, inverter_sn):
        return Battery(self.__get(f'api/v1/inverter/battery/{inverter_sn}/realtime?sn={inverter_sn}&lan')
                       .json()['data'])

    def __get(self, path):
        return requests.get(self.__url(path), headers=self.__headers(), timeout=20)

    def __headers(self):
        headers = {
            "Content-Type": "application/json"
        }
        if self.access_token:
            headers['Authorization'] = f"Bearer {self.access_token}"
        return headers

    def __login(self):
        payload = {
            'username': self.username,
            'password': self.password,
            'grant_type': 'password',
            'client_id': 'csp-web'
        }
        resp = requests.post(self.__url('oauth/token'), headers={"Content-Type": "application/json"}, timeout=20,
                             json=payload)
        if resp.status_code == 200:
            resp_body = resp.json()
            self.access_token = resp_body['data']['access_token']
            self.refresh_token = resp_body['data']['refresh_token']

    def __url(self, path):
        return f'https://pv.inteless.com/{path}'
