"""Async client for the Sunsynk API."""
import asyncio
import base64
import datetime
import hashlib
import time
from typing import Any

import aiohttp
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

from sunsynk.battery import Battery
from sunsynk.exceptions import (
    InvalidCredentialsException,
    SunsynkAuthenticationError,
    SunsynkConnectionError,
    SunsynkError,
)
from sunsynk.grid import Grid
from sunsynk.input import Input
from sunsynk.inverter import Inverter
from sunsynk.load import Load
from sunsynk.output import Output
from sunsynk.plant import Plant
from sunsynk.weather import Weather

__all__ = [
    'InvalidCredentialsException',
    'SunsynkAuthenticationError',
    'SunsynkClient',
    'SunsynkConnectionError',
    'SunsynkError',
]

DEFAULT_BASE_URL = 'https://api.sunsynk.net'
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=20)


class SunsynkClient:
    """Client for the Sunsynk API.

    Pass an existing ``aiohttp.ClientSession`` as ``session`` to share it with
    the client. The client does not close a shared session. If no session is
    given, the client creates its own session and closes it in ``close()``.
    """

    _SOURCE = 'sunsynk'
    _CLIENT_ID = 'csp-web'

    @classmethod
    async def create(cls, username: str, password: str, base_url: str | None = None,
                     session: aiohttp.ClientSession | None = None) -> 'SunsynkClient':
        """Create a client and log in."""
        self = SunsynkClient(username, password, base_url, session=session)
        return await self.login()

    def __init__(self, username: str, password: str, base_url: str | None = None,
                 session: aiohttp.ClientSession | None = None):
        self.base_url = DEFAULT_BASE_URL if base_url is None else base_url
        self._session = session
        self._close_session = session is None
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.username = username
        self.password = password

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True
        return self._session

    async def __aenter__(self) -> 'SunsynkClient':
        await self.login()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the session if the client created it."""
        if self._session is not None and self._close_session:
            await self._session.close()
            self._session = None

    async def get_plants(self) -> list[Plant]:
        data = await self.__get('api/v1/plants?page=1&limit=10&name=&status=')
        return [Plant(plant) for plant in data['infos']]

    async def get_plant(self, plant_id: int) -> Plant:
        data = await self.__get(f'api/v1/plant/{plant_id}?lan=en&id={plant_id}')
        return Plant(data)

    async def get_weather(self, lon_lat: str, date: str | None = None, lan: str = 'en') -> Weather:
        if date is None:
            date = datetime.date.today().isoformat()
        data = await self.__get(f'api/v1/weather?lan={lan}&date={date}&lonLat={lon_lat}')
        return Weather(data)

    async def get_inverters(self) -> list[Inverter]:
        data = await self.__get('api/v1/inverters?page=1&limit=10&total=0&status=-1&sn=&plantId=&type=-2&softVer=&'
                                'hmiVer=&agentCompanyId=-1&gsn=')
        return [Inverter(inverter) for inverter in data['infos']]

    async def get_inverter_realtime_input(self, inverter_sn: str) -> Input:
        data = await self.__get(f'api/v1/inverter/{inverter_sn}/realtime/input')
        return Input(data)

    async def get_inverter_realtime_output(self, inverter_sn: str) -> Output:
        data = await self.__get(f'api/v1/inverter/{inverter_sn}/realtime/output')
        return Output(data)

    async def get_inverter_realtime_grid(self, inverter_sn: str) -> Grid:
        data = await self.__get(f'api/v1/inverter/grid/{inverter_sn}/realtime?sn={inverter_sn}')
        return Grid(data)

    async def get_inverter_realtime_load(self, inverter_sn: str) -> Load:
        data = await self.__get(f'api/v1/inverter/load/{inverter_sn}/realtime?sn={inverter_sn}')
        return Load(data)

    async def get_inverter_realtime_battery(self, inverter_sn: str) -> Battery:
        data = await self.__get(f'api/v1/inverter/battery/{inverter_sn}/realtime?sn={inverter_sn}&lan')
        return Battery(data)

    async def login(self) -> 'SunsynkClient':
        """Log in and store the access token."""
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
        body = await self.__request('POST', 'oauth/token/new', json=payload)
        if not body.get('success') or not body.get('data'):
            raise SunsynkAuthenticationError()
        self.access_token = body['data'].get('access_token')
        self.refresh_token = body['data'].get('refresh_token')
        if not self.access_token:
            raise SunsynkAuthenticationError()
        return self

    async def __get(self, path: str, attempts: int = 1) -> Any:
        """Perform an authenticated GET and return the ``data`` of the response body."""
        if self.access_token is None:
            await self.login()
        body = await self.__request('GET', path, allow_unauthorized=attempts == 1)
        if body is None:
            # The token expired. Log in again and retry once.
            await self.login()
            return await self.__get(path, attempts=attempts + 1)
        if not body.get('success'):
            raise SunsynkConnectionError(
                f"Sunsynk API request to {path} failed: {body.get('msg', 'unknown error')}"
            )
        return body['data']

    async def __request(self, method: str, path: str, *, json: Any = None,
                        allow_unauthorized: bool = False) -> Any:
        """Perform a request and return the JSON body.

        Returns None for a 401 response when ``allow_unauthorized`` is set, so
        the caller can log in again and retry.
        """
        try:
            async with self.session.request(
                method, self.__url(path), headers=self.__headers(), json=json, timeout=DEFAULT_TIMEOUT
            ) as resp:
                if resp.status == 401:
                    if allow_unauthorized:
                        return None
                    raise SunsynkAuthenticationError()
                if resp.status >= 400:
                    raise SunsynkConnectionError(
                        f'Sunsynk API returned HTTP {resp.status} for {path}'
                    )
                return await resp.json(content_type=None)
        except asyncio.TimeoutError as err:
            raise SunsynkConnectionError(f'Timeout connecting to the Sunsynk API at {self.base_url}') from err
        except aiohttp.ClientError as err:
            raise SunsynkConnectionError(f'Error connecting to the Sunsynk API: {err}') from err
        except ValueError as err:
            raise SunsynkConnectionError('Sunsynk API returned a response that is not JSON') from err

    def __headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers['Authorization'] = f"Bearer {self.access_token}"
        return headers

    async def __fetch_public_key(self) -> str:
        nonce = self.__make_nonce()
        sign = self.__md5_hex(f'nonce={nonce}&source={self._SOURCE}POWER_VIEW')
        body = await self.__request(
            'GET', f'anonymous/publicKey?nonce={nonce}&source={self._SOURCE}&sign={sign}'
        )
        if not body.get('success') or not body.get('data'):
            raise SunsynkConnectionError('Sunsynk API did not return a public key')
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
