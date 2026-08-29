import aiohttp
import pytest

from sunsynk.client import SunsynkClient
from sunsynk.exceptions import (
    InvalidCredentialsException,
    SunsynkApiError,
    SunsynkAuthenticationError,
    SunsynkConnectionError,
    SunsynkError,
)
from tests.mock_api_server import ExpiringTokenMockApiServer, FlakyMockApiServer, MockApiServer


def test_exception_hierarchy():
    assert issubclass(SunsynkAuthenticationError, SunsynkError)
    assert issubclass(SunsynkConnectionError, SunsynkError)
    assert issubclass(SunsynkApiError, SunsynkError)
    assert not issubclass(SunsynkApiError, SunsynkConnectionError)
    assert InvalidCredentialsException is SunsynkAuthenticationError


@pytest.mark.asyncio
async def test_shared_session_is_not_closed(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    test_client = await aiohttp_client(mock_api_server.app)
    base_url = f'http://{test_client.host}:{test_client.port}'

    async with aiohttp.ClientSession() as session:
        client = SunsynkClient('myuser', 'letmein', base_url=base_url, session=session)
        await client.login()
        inverters = await client.get_inverters()
        assert inverters[0].sn == '1029384756'
        await client.close()
        assert not session.closed


@pytest.mark.asyncio
async def test_own_session_is_closed(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()
    session = client.session
    await client.close()
    assert session.closed


@pytest.mark.asyncio
async def test_get_without_login_logs_in_first(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    test_client = await aiohttp_client(mock_api_server.app)
    client = SunsynkClient('myuser', 'letmein', base_url=f'http://{test_client.host}:{test_client.port}')
    inverters = await client.get_inverters()
    assert inverters[0].sn == '1029384756'
    assert client.access_token == 'AT123'
    await client.close()


@pytest.mark.asyncio
async def test_relogin_after_unauthorized(aiohttp_client):
    mock_api_server = FlakyMockApiServer(aiohttp_client)
    client = await mock_api_server.client()
    inverters = await client.get_inverters()
    assert inverters[0].sn == '1029384756'
    assert mock_api_server.login_count == 2


@pytest.mark.asyncio
async def test_unauthorized_after_relogin_raises(aiohttp_client):
    mock_api_server = FlakyMockApiServer(aiohttp_client)
    mock_api_server.unauthorized_responses = 2
    client = await mock_api_server.client()
    with pytest.raises(SunsynkAuthenticationError):
        await client.get_inverters()


@pytest.mark.asyncio
async def test_unsuccessful_body_raises_api_error(aiohttp_client):
    mock_api_server = FlakyMockApiServer(aiohttp_client)
    client = await mock_api_server.client()
    with pytest.raises(SunsynkApiError, match='Something went wrong') as exc_info:
        await client._SunsynkClient__get('api/v1/error')  # pylint: disable=protected-access
    assert exc_info.value.code == 500


@pytest.mark.asyncio
async def test_login_error_includes_api_message(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    with pytest.raises(SunsynkAuthenticationError, match='Invalid username or password'):
        await mock_api_server.client(username='invalid')


@pytest.mark.asyncio
async def test_token_expiry_is_tracked(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()
    assert client.token_expires_at is not None
    assert client.token_is_valid()
    client.token_expires_at = 0
    assert not client.token_is_valid()


@pytest.mark.asyncio
async def test_relogin_before_token_expires(aiohttp_client):
    mock_api_server = ExpiringTokenMockApiServer(aiohttp_client)
    client = await mock_api_server.client()
    assert mock_api_server.login_count == 1
    await client.get_inverters()
    assert mock_api_server.login_count == 2
    assert client.access_token == 'AT2'
    await client.get_inverters()
    assert mock_api_server.login_count == 3


@pytest.mark.asyncio
async def test_http_error_raises_connection_error(aiohttp_client):
    mock_api_server = FlakyMockApiServer(aiohttp_client)
    client = await mock_api_server.client()
    with pytest.raises(SunsynkConnectionError, match='HTTP 500'):
        await client._SunsynkClient__get('api/v1/server-error')  # pylint: disable=protected-access


@pytest.mark.asyncio
async def test_not_json_raises_connection_error(aiohttp_client):
    mock_api_server = FlakyMockApiServer(aiohttp_client)
    client = await mock_api_server.client()
    with pytest.raises(SunsynkConnectionError, match='not JSON'):
        await client._SunsynkClient__get('api/v1/not-json')  # pylint: disable=protected-access


@pytest.mark.asyncio
async def test_unreachable_host_raises_connection_error():
    client = SunsynkClient('myuser', 'letmein', base_url='http://127.0.0.1:1')
    with pytest.raises(SunsynkConnectionError):
        await client.login()
    await client.close()


@pytest.mark.asyncio
async def test_values_are_numeric(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    grid = await client.get_inverter_realtime_grid('1029384756')
    assert grid.today_import == 12.2
    assert grid.total_export == 48.2
    assert grid.get_total_power() == 610.0
    assert grid.get_voltage() == 233.6

    battery = await client.get_inverter_realtime_battery('1029384756')
    assert battery.soc == 20.0
    assert battery.charge_today == 1.1
    assert battery.battery_soc_2 is None
    assert battery.number_of_batteries is None

    solar = await client.get_inverter_realtime_input('1029384756')
    assert solar.get_power() == 9.0
    assert solar.pv_iv[0].vpv == 91.5

    load = await client.get_inverter_realtime_load('1029384756')
    assert load.get_total_power() == 3427.0
    assert load.daily_used == 34.7
