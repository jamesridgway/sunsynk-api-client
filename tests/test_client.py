import datetime

import pytest

from sunsynk.battery import Battery
from sunsynk.client import SunsynkClient, InvalidCredentialsException
from sunsynk.grid import Grid
from sunsynk.input import Input
from sunsynk.plant import Plant
from sunsynk.weather import Weather
from tests.mock_api_server import MockApiServer, PagedMockApiServer


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


def test_weather_missing_current_conditions():
    weather = Weather({})

    assert weather.description is None
    assert weather.get_current_temp() is None
    assert weather.get_wind_speed() is None
    assert weather.get_wind_direction() is None
    assert weather.get_temp_min_c() is None
    assert weather.get_temp_max_c() is None



@pytest.mark.asyncio
async def test_get_user(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    user = await client.get_user()

    assert user.id == 281092
    assert user.email == 'john.smith@example.com'
    assert user.created_at.year == 2022


@pytest.mark.asyncio
async def test_get_inverter(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    inverter = await client.get_inverter('1029384756')

    assert inverter.sn == '1029384756'
    assert inverter.rate_power == 5000.0
    assert inverter.brand == 'Sunsynk'
    assert inverter.generated_month == 120.5
    assert inverter.generated_year == 1500.25
    assert inverter.run_status == 1
    assert inverter.equip_type == 2
    assert inverter.version.comm_ver == '1.0'
    assert inverter.user.id == 281092
    assert inverter.plant.id == 12345
    assert inverter.updated_at.year == 2023
    assert inverter.updated_at.tzinfo is not None


@pytest.mark.asyncio
async def test_get_inverter_flow(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    flow = await client.get_inverter_flow('1029384756')

    assert flow.pv_power == 9.0
    assert flow.battery_power == -18.0
    assert flow.battery_power_2 is None
    assert flow.grid_or_meter_power == 610.0
    assert flow.load_or_eps_power == 3427.0
    assert flow.generator_power == 0.0
    assert flow.soc == 20.0
    assert flow.to_grid is False
    assert flow.bat_to is True
    assert flow.raw['custCode'] == 29


@pytest.mark.asyncio
async def test_get_inverter_temperatures(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    temps = await client.get_inverter_temperatures('1029384756', date='2026-07-07')

    assert temps.get_dc_temp() == 41.3
    assert temps.get_igbt_temp() == 36.5
    assert temps.dc_temp.unit == '℃'
    assert len(temps.dc_temp.records) == 2
    assert temps.dc_temp.records[0].timestamp.hour == 10
    assert temps.get_series('DC Temp') is temps.dc_temp


@pytest.mark.asyncio
async def test_get_inverter_output_day(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    data = await client.get_inverter_output_day('1029384756', ['pac', 'dc_temp'], date=datetime.date(2026, 7, 7))

    assert [s.label for s in data.series] == ['DC Temp', 'pac']
    assert data.get_series('pac').latest_value() == 1200.0
    assert data.get_series('missing') is None
    assert mock_api_server.requests[-1][2]['column'] == 'pac,dc_temp'


@pytest.mark.asyncio
async def test_get_inverter_settings(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    settings = await client.get_inverter_settings('1029384756')

    assert settings.sn == '1029384756'
    assert settings.energy_mode == 1
    assert settings.is_battery_first() is False
    assert settings.sys_work_mode == 2
    assert settings.is_essential_only() is False
    assert settings.battery_low_cap == 20
    assert settings.battery_shutdown_cap == 10
    assert settings.zero_export_power == 20
    assert settings.solar_sell is True
    assert settings.peak_and_valley is True
    assert settings.capacities == [100, 40, 40, 40, 40, 40]
    assert settings.grid_charge_on == [True, False, False, False, False, False]
    assert settings.is_grid_charge_enabled() is True
    assert settings.sell_times[1] == '04:00'
    assert settings.sell_time_power[0] == 5000
    assert settings.days_on['monday'] is True
    assert settings.get('someUnknownSetting') == '42'
    assert settings.raw['beep'] == '0'


@pytest.mark.asyncio
async def test_set_inverter_settings(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    await client.set_inverter_settings('1029384756', {'cap1': '80', 'time1on': True})
    assert mock_api_server.settings_writes[-1] == {'cap1': '80', 'time1on': True, 'sn': '1029384756'}

    settings = await client.get_inverter_settings('1029384756')
    settings.raw['cap1'] = '90'
    await client.set_inverter_settings('1029384756', settings)
    assert mock_api_server.settings_writes[-1]['cap1'] == '90'
    assert mock_api_server.settings_writes[-1]['sn'] == '1029384756'


@pytest.mark.asyncio
async def test_get_plant_realtime(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    realtime = await client.get_plant_realtime(12345)

    assert realtime.pac == 2484.0
    assert realtime.efficiency == 0.75
    assert realtime.generation_today == 9.0
    assert realtime.generation_month == 120.5
    assert realtime.generation_year == 1500.25
    assert realtime.generation_total == 5622.3
    assert realtime.income == 12.34
    assert realtime.currency.code == 'GBP'
    assert realtime.updated_at.year == 2023


@pytest.mark.asyncio
async def test_get_plant_energy(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    day = await client.get_plant_energy_day(12345, date='2026-07-07')
    assert day.get_series('PV').latest_value() == 200.0
    assert day.get_series('Load').records[0].value == 300.0

    month = await client.get_plant_energy_month(12345, date=datetime.date(2026, 7, 1))
    assert month.get_series('PV').unit == 'kWh'
    assert [r.value for r in month.get_series('PV').records] == [10.5, 12.0]


@pytest.mark.asyncio
async def test_set_plant_income(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    await client.set_plant_income(12345, {'currency': 'GBP', 'price': 0.25})
    assert mock_api_server.income_writes == [{'currency': 'GBP', 'price': 0.25}]


@pytest.mark.asyncio
async def test_pagination_fetches_all_pages(aiohttp_client):
    mock_api_server = PagedMockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    inverters = await client.get_inverters()
    assert len(inverters) == 25
    assert inverters[0].sn == 'SN000'
    assert inverters[-1].sn == 'SN024'
    inverter_pages = [q['page'] for _, path, q in mock_api_server.requests if path == '/api/v1/inverters']
    assert inverter_pages == ['1', '2', '3']

    plants = await client.get_plants()
    assert len(plants) == 12
    assert plants[-1].id == 11


@pytest.mark.asyncio
async def test_pagination_single_page(aiohttp_client):
    mock_api_server = PagedMockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    inverters = await client.get_inverters(page=2, limit=10)
    assert [i.sn for i in inverters] == [f'SN{i:03d}' for i in range(10, 20)]

    plants = await client.get_plants(page=1, limit=5)
    assert len(plants) == 5


@pytest.mark.asyncio
async def test_battery_extra_fields(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    battery = await client.get_inverter_realtime_battery('1029384756')
    assert battery.get_soc() == battery.soc
    assert battery.soc_2 is None
    assert mock_api_server.requests[-1][2] == {'sn': '1029384756', 'lan': 'en'}


def test_battery_prefers_bms_soc():
    battery = Battery({'soc': '19', 'bmsSoc': 21, 'bmsVolt': '53.1'})
    assert battery.get_soc() == 21.0
    assert battery.bms_voltage == 53.1


def test_grid_relay_status():
    assert Grid({'acRealyStatus': 1}).is_connected() is True
    assert Grid({'acRealyStatus': 0}).is_connected() is False
    assert Grid({}).is_connected() is None


def test_input_power_falls_back_to_pac():
    assert Input({'pac': 1234}).get_power() == 1234.0
    assert Input({'pac': 1234, 'mpptIV': [{'ppv': '100'}, {'ppv': '50'}]}).get_power() == 150.0
    assert Input({}).get_power() == 0.0


def test_plant_numeric_conversion_and_missing_fields():
    plant = Plant({'id': '12345', 'name': 'x', 'pac': '2484', 'lon': '-0.72', 'lat': '51.3',
                   'updateAt': '2023-01-07T16:50:17.123+01:00'})
    assert plant.id == 12345
    assert plant.pac == 2484.0
    assert plant.lon == -0.72
    assert plant.updated_at.utcoffset().total_seconds() == 3600

    empty = Plant({})
    assert empty.id is None
    assert empty.name is None
    assert empty.updated_at is None


@pytest.mark.asyncio
async def test_battery_presence(aiohttp_client):
    mock_api_server = MockApiServer(aiohttp_client)
    client = await mock_api_server.client()

    battery = await client.get_inverter_realtime_battery('1029384756')
    assert battery.is_present is True

    mock_api_server.battery_connected = False
    battery = await client.get_inverter_realtime_battery('1029384756')
    assert battery.is_present is False
    assert battery.voltage == 0.0


def test_battery_presence_from_count():
    assert Battery({'batteryNum': 2}).is_present is True
    assert Battery({'batteryNum': 2}).number_of_batteries == 2
    assert Battery({'numberOfBatteries': 0, 'voltage': None}).is_present is False
    assert Battery({'voltage': '0.0', 'bmsVolt': '53.1'}).is_present is True
