import pytest

from sunsynk.client import SunsynkClient, InvalidCredentialsException
from sunsynk.weather import Weather
from tests.mock_api_server import MockApiServer



@pytest.mark.asyncio
async def test_login(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()
    assert isinstance(client, SunsynkClient)


@pytest.mark.asyncio
async def test_login_invalid(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    with pytest.raises(InvalidCredentialsException):
        await mock_api_server.client(username='invalid')

@pytest.mark.asyncio
async def test_get_inverters(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    inverters = await client.get_inverters()

    assert inverters[0].sn == '1029384756'
    assert inverters[0].gsn == 'E0192837465'


@pytest.mark.asyncio
async def test_get_plants(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    plants = await client.get_plants()

    assert plants[0].id == 12345
    assert plants[0].name == 'John Smith'

@pytest.mark.asyncio
async def test_get_inverter_realtime_input(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    inverters = await client.get_inverters()
    input = await client.get_inverter_realtime_input(inverters[0].sn)

    assert input.get_power() == 9.0


@pytest.mark.asyncio
async def test_get_inverter_realtime_output(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    inverters = await client.get_inverters()
    output = await client.get_inverter_realtime_output(inverters[0].sn)

    assert output.vip[0].voltage == 230.8
    assert output.vip[0].current == 0.3
    assert output.vip[0].power == -50

@pytest.mark.asyncio
async def test_get_inverter_realtime_grid(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    inverters = await client.get_inverters()
    grid = await client.get_inverter_realtime_grid(inverters[0].sn)

    assert grid.get_power() == 610
    assert grid.get_current() == 0.8
    assert grid.get_voltage() == 233.6

@pytest.mark.asyncio
async def test_get_inverter_realtime_battery(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    inverters = await client.get_inverters()
    battery = await client.get_inverter_realtime_battery(inverters[0].sn)

    assert battery.power == -18
    assert battery.get_power() == -18
    assert battery.get_current() == -0.4
    assert battery.get_voltage() == 53.3


@pytest.mark.asyncio
async def test_get_inverter_realtime_load(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    inverters = await client.get_inverters()
    load = await client.get_inverter_realtime_load(inverters[0].sn)

    assert load.total_used == 3133.10
    assert load.daily_used == 34.70
    assert load.total_power == 3427
    assert load.smart_load_status == -1
    assert load.load_fac == 50.01
    assert load.ups_power_l1 == 5.0
    assert load.ups_power_l2 == 0.0
    assert load.ups_power_l3 == 0.0
    assert load.ups_power_total == 5.0

    assert load.get_voltage() == 246.6
    assert load.get_current() == 0.0
    assert load.get_power() == 3427.0

    load.vip = []
    assert load.get_voltage() is None
    assert load.get_current() is None
    assert load.get_power() is None


@pytest.mark.asyncio
async def test_get_plant(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    plant = await client.get_plant(12345)

    assert plant.id == 12345
    assert plant.name == 'John Smith'
    assert plant.lon == -0.724613
    assert plant.lat == 51.322984
    assert plant.generation_today == 9.00
    assert plant.generation_total == 5622.30
    assert plant.pac == 2484
    assert plant.master_id == 54321


@pytest.mark.asyncio
async def test_get_weather(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    plant = await client.get_plant(12345)
    lon_lat = f"{plant.lat},{plant.lon}"
    assert lon_lat == "51.322984,-0.724613"

    weather = await client.get_weather(lon_lat, date="2026-07-07")

    assert isinstance(weather, Weather)
    assert weather.description == "broken clouds"
    assert weather.get_current_temp() == 20.6
    assert weather.get_wind_speed() == 3.9
    assert weather.get_wind_direction() == 292
    assert weather.sunrise == "04:55"
    assert weather.sunset == "21:19"
    assert weather.icon_url == "https://sunsynk-s3.s3.eu-west-2.amazonaws.com/weather/openweather/04d.png"
    assert weather.get_temp_min_c() == 19.7
    assert weather.get_temp_max_c() == 21.8

