import pytest

from sunsynk.client import SunsynkClient, InvalidCredentialsException
from tests.mock_api_server import MockApiServer


@pytest.mark.asyncio
async def test_login(aiohttp_client, event_loop):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()
    assert isinstance(client, SunsynkClient)


@pytest.mark.asyncio
async def test_login_invalid(aiohttp_client, event_loop):
    mock_api_server = MockApiServer(aiohttp_client)
    with pytest.raises(InvalidCredentialsException):
        await mock_api_server.client(username='invalid')

@pytest.mark.asyncio
async def test_get_inverters(aiohttp_client, event_loop):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    inverters = await client.get_inverters()

    assert inverters[0].sn == '1029384756'
    assert inverters[0].gsn == 'E0192837465'


@pytest.mark.asyncio
async def test_get_plants(aiohttp_client, event_loop):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    plants = await client.get_plants()

    assert plants[0].id == 12345
    assert plants[0].name == 'John Smith'

@pytest.mark.asyncio
async def test_get_inverter_realtime_input(aiohttp_client, event_loop):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    inverters = await client.get_inverters()
    input = await client.get_inverter_realtime_input(inverters[0].sn)

    assert input.get_power() == 9.0


@pytest.mark.asyncio
async def test_get_inverter_realtime_output(aiohttp_client, event_loop):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    inverters = await client.get_inverters()
    output = await client.get_inverter_realtime_output(inverters[0].sn)

    assert output.vip[0].voltage == 230.8
    assert output.vip[0].current == 0.3
    assert output.vip[0].power == -50

@pytest.mark.asyncio
async def test_get_inverter_realtime_grid(aiohttp_client, event_loop):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    inverters = await client.get_inverters()
    grid = await client.get_inverter_realtime_grid(inverters[0].sn)

    assert grid.get_power() == 610
    assert grid.get_current() == 0.8
    assert grid.get_voltage() == 233.6

@pytest.mark.asyncio
async def test_get_inverter_realtime_battery(aiohttp_client, event_loop):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    inverters = await client.get_inverters()
    battery = await client.get_inverter_realtime_battery(inverters[0].sn)

    assert battery.power == -18
    assert battery.get_power() == -18
    assert battery.get_current() == -0.4
    assert battery.get_voltage() == 53.3
