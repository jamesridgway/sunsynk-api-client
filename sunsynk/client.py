import json

import aiohttp

from sunsynk.battery import Battery
from sunsynk.grid import Grid
from sunsynk.input import Input
from sunsynk.inverter import Inverter
from sunsynk.output import Output
from sunsynk.plant import Plant


class SunsynkClient:

    @classmethod
    async def create(cls, username, password, base_url=None):
        self = SunsynkClient(username, password, base_url)
        return await self.login()

    def __init__(self, username, password, base_url=None):
        self.base_url = 'https://pv.inteless.com' if base_url is None else base_url
        self.session = aiohttp.ClientSession()
        self.access_token = None
        self.refresh_token = None
        self.username = username
        self.password = password

    async def __aenter__(self):
        await self.login()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self):
        await self.session.close()

    async def get_plants(self):
        resp = await self.__get('api/v1/plants?page=1&limit=10&name=&status=')
        json = await resp.json()
        plants = json['data']['infos']
        return [Plant(data) for data in plants]

    async def get_inverters(self):
        resp = await self.__get('api/v1/inverters?page=1&limit=10&total=0&status=-1&sn=&plantId=&type=-2&softVer=&' \
                   'hmiVer=&agentCompanyId=-1&gsn=')
        body = await resp.json()
        print(json.dumps(body))
        inverters = body['data']['infos']
        return [Inverter(data) for data in inverters]

    async def get_inverter_realtime_input(self, inverter_sn):
        resp = await self.__get(f'api/v1/inverter/{inverter_sn}/realtime/input')
        json = await resp.json()
        return Input(json['data'])

    async def get_inverter_realtime_output(self, inverter_sn):
        resp = await self.__get(f'api/v1/inverter/{inverter_sn}/realtime/output')
        json = await resp.json()
        return Output(json['data'])

    async def get_inverter_realtime_grid(self, inverter_sn):
        resp = await self.__get(f'api/v1/inverter/grid/{inverter_sn}/realtime?sn={inverter_sn}')
        json = await resp.json()
        return Grid(json['data'])

    async def get_inverter_realtime_battery(self, inverter_sn):
        resp = await self.__get(f'api/v1/inverter/battery/{inverter_sn}/realtime?sn={inverter_sn}&lan')
        json = await resp.json()
        return Battery(json['data'])

    async def __get(self, path):
        return await self.session.get(self.__url(path), headers=self.__headers(), timeout=20)

    def __headers(self):
        headers = {
            "Content-Type": "application/json"
        }
        if self.access_token:
            headers['Authorization'] = f"Bearer {self.access_token}"
        return headers

    async def login(self):
        payload = {
            'username': self.username,
            'password': self.password,
            'grant_type': 'password',
            'client_id': 'csp-web'
        }
        resp = await self.session.post(self.__url('oauth/token'),
                                 headers={"Content-Type": "application/json"},
                                 timeout=20,
                                 json=payload)
        if resp.status == 200:
            resp_body = await resp.json()
            self.access_token = resp_body['data']['access_token']
            self.refresh_token = resp_body['data']['refresh_token']
        return self

    def __url(self, path):
        return f'{self.base_url}/{path}'
