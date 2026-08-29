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
    SunsynkApiError,
    SunsynkAuthenticationError,
    SunsynkConnectionError,
    SunsynkError,
)
from sunsynk.flow import Flow
from sunsynk.grid import Grid
from sunsynk.input import Input
from sunsynk.inverter import Inverter, InverterDetails
from sunsynk.load import Load
from sunsynk.output import Output
from sunsynk.plant import Plant, PlantRealtime
from sunsynk.series import InverterTemperatures, SeriesData
from sunsynk.settings import Settings
from sunsynk.user import User
from sunsynk.weather import Weather

__all__ = [
    'InvalidCredentialsException',
    'SunsynkApiError',
    'SunsynkAuthenticationError',
    'SunsynkClient',
    'SunsynkConnectionError',
    'SunsynkError',
]

DEFAULT_BASE_URL = 'https://api.sunsynk.net'
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=20)
DEFAULT_PAGE_SIZE = 10
# Log in again this many seconds before the access token is due to expire.
TOKEN_EXPIRY_MARGIN = 300


class SunsynkClient:  # pylint: disable=too-many-public-methods
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
        self.base_url = DEFAULT_BASE_URL if base_url is None else base_url.rstrip('/')
        self._session = session
        self._close_session = session is None
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.token_expires_at: float | None = None
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

    # ------------------------------------------------------------------ user

    async def get_user(self, lan: str = 'en') -> User:
        """Return the user account that is logged in."""
        data = await self.__get('api/v1/user', params={'lan': lan})
        return User(data)

    # ---------------------------------------------------------------- plants

    async def get_plants(self, page: int | None = None, limit: int = DEFAULT_PAGE_SIZE) -> list[Plant]:
        """Return the plants visible to the account.

        With no ``page`` every page is fetched and all plants are returned.
        Pass ``page`` (1-based) to fetch a single page of ``limit`` plants.
        """
        infos = await self.__get_paged('api/v1/plants', {'name': '', 'status': ''}, page, limit)
        return [Plant(plant) for plant in infos]

    async def get_plant(self, plant_id: int) -> Plant:
        """Return the full details of a plant, including its coordinates."""
        data = await self.__get(f'api/v1/plant/{plant_id}', params={'lan': 'en', 'id': plant_id})
        return Plant(data)

    async def get_plant_realtime(self, plant_id: int) -> PlantRealtime:
        """Return the realtime totals (power, generation, income) for a plant."""
        data = await self.__get(f'api/v1/plant/{plant_id}/realtime', params={'id': plant_id})
        return PlantRealtime(data)

    async def get_plant_energy_day(self, plant_id: int, date: str | datetime.date | None = None,
                                   lan: str = 'en') -> SeriesData:
        """Return the 5-minute energy series for a plant for one day (``YYYY-MM-DD``)."""
        data = await self.__get(f'api/v1/plant/energy/{plant_id}/day',
                                params={'lan': lan, 'date': self.__format_date(date), 'id': plant_id})
        return SeriesData(data)

    async def get_plant_energy_month(self, plant_id: int, date: str | datetime.date | None = None,
                                     lan: str = 'en') -> SeriesData:
        """Return the daily energy series for a plant for one month (``YYYY-MM``)."""
        data = await self.__get(f'api/v1/plant/energy/{plant_id}/month',
                                params={'lan': lan, 'date': self.__format_date(date, '%Y-%m'), 'id': plant_id})
        return SeriesData(data)

    async def set_plant_income(self, plant_id: int, settings: dict[str, Any]) -> None:
        """Update the income/tariff settings of a plant.

        ``settings`` is posted as-is to ``api/v1/plant/{id}/income``.
        """
        await self.__post(f'api/v1/plant/{plant_id}/income', settings)

    async def get_weather(self, lon_lat: str, date: str | datetime.date | None = None, lan: str = 'en') -> Weather:
        """Return the weather for a location given as ``"lat,lon"``."""
        data = await self.__get('api/v1/weather',
                                params={'lan': lan, 'date': self.__format_date(date), 'lonLat': lon_lat})
        return Weather(data)

    # ------------------------------------------------------------- inverters

    async def get_inverters(self, page: int | None = None, limit: int = DEFAULT_PAGE_SIZE) -> list[Inverter]:
        """Return the inverters visible to the account.

        With no ``page`` every page is fetched and all inverters are returned.
        Pass ``page`` (1-based) to fetch a single page of ``limit`` inverters.
        """
        params = {'total': 0, 'status': -1, 'sn': '', 'plantId': '', 'type': -2, 'softVer': '',
                  'hmiVer': '', 'agentCompanyId': -1, 'gsn': ''}
        infos = await self.__get_paged('api/v1/inverters', params, page, limit)
        return [Inverter(inverter) for inverter in infos]

    async def get_inverter(self, inverter_sn: str) -> InverterDetails:
        """Return the full details of one inverter (rated power, brand, monthly/yearly generation...)."""
        data = await self.__get(f'api/v1/inverter/{inverter_sn}')
        return InverterDetails(data)

    async def get_inverter_flow(self, inverter_sn: str) -> Flow:
        """Return the energy flow (PV, battery, grid, load, generator power and SOC) in one request."""
        data = await self.__get(f'api/v1/inverter/{inverter_sn}/flow')
        return Flow(data)

    async def get_inverter_realtime_input(self, inverter_sn: str) -> Input:
        data = await self.__get(f'api/v1/inverter/{inverter_sn}/realtime/input')
        return Input(data)

    async def get_inverter_realtime_output(self, inverter_sn: str) -> Output:
        data = await self.__get(f'api/v1/inverter/{inverter_sn}/realtime/output')
        return Output(data)

    async def get_inverter_realtime_grid(self, inverter_sn: str) -> Grid:
        data = await self.__get(f'api/v1/inverter/grid/{inverter_sn}/realtime', params={'sn': inverter_sn})
        return Grid(data)

    async def get_inverter_realtime_load(self, inverter_sn: str) -> Load:
        data = await self.__get(f'api/v1/inverter/load/{inverter_sn}/realtime', params={'sn': inverter_sn})
        return Load(data)

    async def get_inverter_realtime_battery(self, inverter_sn: str) -> Battery:
        data = await self.__get(f'api/v1/inverter/battery/{inverter_sn}/realtime',
                                params={'sn': inverter_sn, 'lan': 'en'})
        return Battery(data)

    async def get_inverter_output_day(self, inverter_sn: str, columns: list[str] | str,
                                      date: str | datetime.date | None = None, lan: str = 'en') -> SeriesData:
        """Return the history of one or more output columns for an inverter for one day.

        ``columns`` are API column names such as ``dc_temp``, ``igbt_temp``,
        ``pac`` or ``vac1``.
        """
        if not isinstance(columns, str):
            columns = ','.join(columns)
        data = await self.__get(f'api/v1/inverter/{inverter_sn}/output/day',
                                params={'lan': lan, 'date': self.__format_date(date), 'column': columns})
        return SeriesData(data)

    async def get_inverter_temperatures(self, inverter_sn: str,
                                        date: str | datetime.date | None = None) -> InverterTemperatures:
        """Return the DC and IGBT (AC) temperature history of an inverter for one day."""
        data = await self.__get(f'api/v1/inverter/{inverter_sn}/output/day',
                                params={'lan': 'en', 'date': self.__format_date(date),
                                        'column': 'dc_temp,igbt_temp'})
        return InverterTemperatures(data)

    async def get_inverter_settings(self, inverter_sn: str) -> Settings:
        """Return the settings of an inverter (work mode, timer slots, battery capacities...)."""
        data = await self.__get(f'api/v1/common/setting/{inverter_sn}/read')
        return Settings(data)

    async def set_inverter_settings(self, inverter_sn: str, settings: Settings | dict[str, Any]) -> None:
        """Write settings to an inverter.

        Pass a ``Settings`` object (its ``raw`` dict is sent) or a dict of the
        API setting names to change. The Sunsynk API requires an installer
        account to change settings.
        """
        payload = settings.raw if isinstance(settings, Settings) else dict(settings)
        payload.setdefault('sn', inverter_sn)
        await self.__post(f'api/v1/common/setting/{inverter_sn}/set', payload)

    # ------------------------------------------------------------------ auth

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
        data = body.get('data') if isinstance(body, dict) else None
        if not body.get('success') or not data:
            raise SunsynkAuthenticationError(self.__login_failure_message(body))
        self.access_token = data.get('access_token')
        self.refresh_token = data.get('refresh_token')
        expires_in = data.get('expires_in')
        if isinstance(expires_in, (int, float)) and expires_in > 0:
            self.token_expires_at = time.time() + expires_in
        else:
            self.token_expires_at = None
        if not self.access_token:
            raise SunsynkAuthenticationError(self.__login_failure_message(body))
        return self

    def token_is_valid(self) -> bool:
        """Return True if there is an access token that is not about to expire."""
        if not self.access_token:
            return False
        if self.token_expires_at is None:
            return True
        return time.time() < self.token_expires_at - TOKEN_EXPIRY_MARGIN

    @staticmethod
    def __login_failure_message(body: Any) -> str:
        msg = body.get('msg') if isinstance(body, dict) else None
        code = body.get('code') if isinstance(body, dict) else None
        if msg:
            return f'Sunsynk API rejected the login: {msg}' + (f' (code {code})' if code is not None else '')
        return 'Invalid username or password'

    # -------------------------------------------------------------- requests

    async def __get_paged(self, path: str, params: dict[str, Any], page: int | None, limit: int) -> list[Any]:
        if page is not None:
            data = await self.__get(path, params={'page': page, 'limit': limit, **params})
            return list(data.get('infos') or [])
        infos: list[Any] = []
        current = 1
        while True:
            data = await self.__get(path, params={'page': current, 'limit': limit, **params})
            page_infos = list(data.get('infos') or [])
            infos.extend(page_infos)
            total = data.get('total')
            if not page_infos or len(page_infos) < limit:
                break
            if isinstance(total, int) and len(infos) >= total:
                break
            current += 1
        return infos

    async def __get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Perform an authenticated GET and return the ``data`` of the response body."""
        return await self.__authenticated('GET', path, params=params)

    async def __post(self, path: str, json: Any) -> Any:
        """Perform an authenticated POST and return the ``data`` of the response body."""
        return await self.__authenticated('POST', path, json=json)

    async def __authenticated(  # pylint: disable=too-many-arguments
            self, method: str, path: str, *, params: dict[str, Any] | None = None,
            json: Any = None, attempts: int = 1) -> Any:
        if not self.token_is_valid():
            await self.login()
        body = await self.__request(method, path, params=params, json=json, allow_unauthorized=attempts == 1)
        if body is None:
            # The token was rejected. Log in again and retry once.
            await self.login()
            return await self.__authenticated(method, path, params=params, json=json, attempts=attempts + 1)
        if not isinstance(body, dict):
            raise SunsynkConnectionError(f'Sunsynk API returned an unexpected response for {path}')
        if not body.get('success'):
            raise SunsynkApiError(
                f"Sunsynk API request to {path} failed: {body.get('msg', 'unknown error')}",
                code=body.get('code'),
            )
        return body.get('data')

    async def __request(  # pylint: disable=too-many-arguments
            self, method: str, path: str, *, params: dict[str, Any] | None = None,
            json: Any = None, allow_unauthorized: bool = False) -> Any:
        """Perform a request and return the JSON body.

        Returns None for a 401 response when ``allow_unauthorized`` is set, so
        the caller can log in again and retry.
        """
        if params is not None:
            params = {k: ('' if v is None else str(v)) for k, v in params.items()}
        try:
            async with self.session.request(
                method, self.__url(path), headers=self.__headers(), params=params, json=json,
                timeout=DEFAULT_TIMEOUT
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
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if self.access_token:
            headers['Authorization'] = f"Bearer {self.access_token}"
        return headers

    async def __fetch_public_key(self) -> str:
        nonce = self.__make_nonce()
        sign = self.__md5_hex(f'nonce={nonce}&source={self._SOURCE}POWER_VIEW')
        body = await self.__request(
            'GET', 'anonymous/publicKey', params={'nonce': nonce, 'source': self._SOURCE, 'sign': sign}
        )
        if not isinstance(body, dict) or not body.get('success') or not body.get('data'):
            raise SunsynkConnectionError('Sunsynk API did not return a public key')
        return body['data']

    @staticmethod
    def __format_date(date: str | datetime.date | None, fmt: str = '%Y-%m-%d') -> str:
        if date is None:
            date = datetime.date.today()
        if isinstance(date, (datetime.date, datetime.datetime)):
            return date.strftime(fmt)
        return date

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
