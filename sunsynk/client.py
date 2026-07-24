import base64
import datetime
import hashlib
import time

import aiohttp
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

from sunsynk.battery import Battery
from sunsynk.grid import Grid
from sunsynk.input import Input
from sunsynk.inverter import Inverter
from sunsynk.load import Load
from sunsynk.output import Output
from sunsynk.plant import Plant
from sunsynk.weather import Weather


class InvalidCredentialsException(Exception):
    def __init__(self):
        super().__init__('Invalid username or password')


class SunsynkClient:

    _SOURCE = 'sunsynk'
    _CLIENT_ID = 'csp-web'

    @classmethod
    async def create(cls, username: str, password: str, base_url: str = None):
        self = SunsynkClient(username, password, base_url)
        return await self.login()

    def __init__(self, username: str, password: str, base_url: str=None):
        self.base_url = 'https://api.sunsynk.net' if base_url is None else base_url
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

    async def get_plants(self) -> list[Plant]:
        resp = await self.__get('api/v1/plants?page=1&limit=10&name=&status=')
        body = await resp.json()
        plants = body['data']['infos']
        return [Plant(data) for data in plants]

    async def get_plant(self, plant_id: int) -> Plant:
        resp = await self.__get(f'api/v1/plant/{plant_id}?lan=en&id={plant_id}')
        body = await resp.json()
        return Plant(body['data'])

    async def get_weather(self, lon_lat: str, date: str = None, lan: str = 'en') -> Weather:
        if date is None:
            date = datetime.date.today().isoformat()
        resp = await self.__get(f'api/v1/weather?lan={lan}&date={date}&lonLat={lon_lat}')
        body = await resp.json()
        return Weather(body['data'])

    async def get_inverters(self) -> list[Inverter]:
        resp = await self.__get('api/v1/inverters?page=1&limit=10&total=0&status=-1&sn=&plantId=&type=-2&softVer=&' \
                                'hmiVer=&agentCompanyId=-1&gsn=')
        body = await resp.json()
        inverters = body['data']['infos']
        return [Inverter(data) for data in inverters]

    async def get_inverter_realtime_input(self, inverter_sn: str) -> Input:
        resp = await self.__get(f'api/v1/inverter/{inverter_sn}/realtime/input')
        body = await resp.json()
        return Input(body['data'])

    async def get_inverter_realtime_output(self, inverter_sn: str) -> Output:
        resp = await self.__get(f'api/v1/inverter/{inverter_sn}/realtime/output')
        body = await resp.json()
        return Output(body['data'])

    async def get_inverter_realtime_grid(self, inverter_sn: str) -> Grid:
        resp = await self.__get(f'api/v1/inverter/grid/{inverter_sn}/realtime?sn={inverter_sn}')
        body = await resp.json()
        return Grid(body['data'])

    async def get_inverter_realtime_load(self, inverter_sn: str) -> Load:
        resp = await self.__get(f'api/v1/inverter/load/{inverter_sn}/realtime?sn={inverter_sn}')
        body = await resp.json()
        return Load(body['data'])

    async def get_inverter_realtime_battery(self, inverter_sn: str) -> Battery:
        resp = await self.__get(f'api/v1/inverter/battery/{inverter_sn}/realtime?sn={inverter_sn}&lan')
        body = await resp.json()
        return Battery(body['data'])

    async def __get(self, path: str, attempts: int = 1):
        resp = await self.session.get(self.__url(path), headers=self.__headers(), timeout=20)
        if resp.status == 401 and attempts == 1:
            await self.login()
            return await self.__get(path, attempts=attempts + 1)
        return resp

    def __headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json"
        }
        if self.access_token:
            headers['Authorization'] = f"Bearer {self.access_token}"
        return headers

    async def login(self):
        raw_key = await self.__fetch_public_key()
        encrypted_password = self.__rsa_encrypt_pkcs1v15(raw_key, self.password)

        login_nonce = self.__make_nonce()
        login_sign = self.__md5_hex(
            f'nonce={login_nonce}&source={self._SOURCE}{raw_key[:10]}'
        )
        payload = {
            'username': self.username,
            'password': encrypted_password,
            'grant_type': 'password',
            'client_id': self._CLIENT_ID,
            'source': self._SOURCE,
            'nonce': login_nonce,
            'sign': login_sign,
        }
        resp = await self.session.post(self.__url('oauth/token/new'),
                                       headers={"Content-Type": "application/json"},
                                       timeout=20,
                                       json=payload)
        if resp.status == 200:
            resp_body = await resp.json()
            if resp_body['success']:
                self.access_token = resp_body['data']['access_token']
                self.refresh_token = resp_body['data']['refresh_token']
                return self
        raise InvalidCredentialsException()

    async def __fetch_public_key(self) -> str:
        nonce = self.__make_nonce()
        sign = self.__md5_hex(f'nonce={nonce}&source={self._SOURCE}POWER_VIEW')
        url = self.__url(
            f'anonymous/publicKey?nonce={nonce}&source={self._SOURCE}&sign={sign}'
        )
        resp = await self.session.get(
            url,
            headers={"Content-Type": "application/json"},
            timeout=20,
        )
        if resp.status != 200:
            raise InvalidCredentialsException()
        body = await resp.json()
        if not body.get('success') or not body.get('data'):
            raise InvalidCredentialsException()
        return body['data']

    @staticmethod
    def __make_nonce() -> int:
        return int(time.time() * 1000)

    @staticmethod
    def __md5_hex(value: str) -> str:
        return hashlib.md5(value.encode()).hexdigest()

    @staticmethod
    def __rsa_encrypt_pkcs1v15(raw_key: str, plaintext: str) -> str:
        pem = f'-----BEGIN PUBLIC KEY-----\n{raw_key}\n-----END PUBLIC KEY-----'.encode()
        public_key = serialization.load_pem_public_key(pem)
        ciphertext = public_key.encrypt(plaintext.encode(), padding.PKCS1v15())
        return base64.b64encode(ciphertext).decode()

    def __url(self, path: str) -> str:
        return f'{self.base_url}/{path}'
