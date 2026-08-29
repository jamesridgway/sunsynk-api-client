# Sunsynk API Client
[![CI](https://github.com/jamesridgway/sunsynk-api-client/actions/workflows/ci.yml/badge.svg)](https://github.com/jamesridgway/sunsynk-api-client/actions/workflows/ci.yml)

An API client library for reading data from the Sunsynk API (`api.sunsynk.net`) that is used by the
Sunsynk Connect apps and the [Sunsynk Connect](https://sunsynk.net/) web portal.

This is the API behind the apps, not the licensed Sunsynk OpenAPI (`openapi.sunsynk.net`), which uses a
different authentication scheme.


## Install

    pip install sunsynk-api-client

## Example Usage

    import asyncio
    import os
    
    from sunsynk.client import SunsynkClient
    
    
    async def main():
        sunsynk_username = os.getenv('SUNSYNK_USERNAME')
        sunsynk_password = os.getenv('SUNSYNK_PASSWORD')
    
        async with SunsynkClient(sunsynk_username, sunsynk_password) as client:
            inverters = await client.get_inverters()
            for inverter in inverters:
                grid = await client.get_inverter_realtime_grid(inverter.sn)
                battery = await client.get_inverter_realtime_battery(inverter.sn)
                solar_pv = await client.get_inverter_realtime_input(inverter.sn)
    
                await client.get_inverter_realtime_output(inverter.sn)
    
                print(f"Inverter (sn: {inverter.sn}) is drawing {grid.get_power()}W from the grid, {battery.power}W from battery and {solar_pv.get_power()}W from solar.")
    
        print('Done!')
    
    asyncio.run(main())


## Use With an Existing aiohttp Session

Pass a `session` to share an existing `aiohttp.ClientSession`. The client does
not close a shared session:

    async with aiohttp.ClientSession() as session:
        client = SunsynkClient(sunsynk_username, sunsynk_password, session=session)
        await client.login()
        inverters = await client.get_inverters()

`SunsynkClient.create(username, password)` creates a client and logs in in one step. Pass
`base_url` to talk to a different server. The client logs in again automatically when the access
token is about to expire or is rejected by the API.

## Energy Flow

`get_inverter_flow` returns every power value in one request, and is the only endpoint that
reports generator power:

    flow = await client.get_inverter_flow(inverter.sn)
    print(f"PV {flow.pv_power}W, battery {flow.battery_power}W, grid {flow.grid_or_meter_power}W, "
          f"load {flow.load_or_eps_power}W, generator {flow.generator_power}W, SOC {flow.soc}%")

## Inverter Details, Temperatures and Settings

    # Rated power, brand, monthly and yearly generation, ...
    details = await client.get_inverter(inverter.sn)
    print(f"{details.brand} {details.model} rated at {details.rate_power}W")

    # DC and IGBT (AC) temperature history for today
    temps = await client.get_inverter_temperatures(inverter.sn)
    print(f"DC {temps.get_dc_temp()}C, IGBT {temps.get_igbt_temp()}C")

    # Any output column(s) for a given day, e.g. pac, vac1, dc_temp
    history = await client.get_inverter_output_day(inverter.sn, ['pac'], date='2026-07-07')
    for record in history.get_series('pac').records:
        print(record.timestamp, record.value)

    # Inverter settings (work mode, timer slots, battery capacities, ...)
    settings = await client.get_inverter_settings(inverter.sn)
    print(settings.is_battery_first(), settings.capacities, settings.grid_charge_on)
    print(settings.get('zeroExportPower'))  # any setting by its API name

Settings can be written with `set_inverter_settings`. Pass a dict of the API setting names to
change, or a modified `Settings` object. The Sunsynk API only allows installer accounts to
change settings:

    await client.set_inverter_settings(inverter.sn, {'cap1': '80', 'time1on': True})

## Plants

    plants = await client.get_plants()               # every plant, all pages
    plant = await client.get_plant(plant_id)         # full details, including lon/lat
    realtime = await client.get_plant_realtime(plant_id)  # pac, etoday/emonth/eyear/etotal, income
    day = await client.get_plant_energy_day(plant_id, date='2026-07-07')      # 5-minute series
    month = await client.get_plant_energy_month(plant_id, date='2026-07')      # daily series

`get_inverters()` and `get_plants()` fetch every page by default. Pass `page` (and optionally
`limit`) to fetch a single page.

## Errors

All errors raised by the client subclass `sunsynk.exceptions.SunsynkError`:

* `SunsynkAuthenticationError` - the username or password is not correct.
* `SunsynkConnectionError` - the API could not be reached, timed out, or
  returned an HTTP error or a response that is not JSON.
* `SunsynkApiError` - the API was reached but reported that the request
  failed (`success: false`). The API's `code` is available as `error.code`.
  Retrying is unlikely to help.

Numeric values in the API responses are converted to `float` or `int`. Values
that are missing are `None`. Timestamps are timezone-aware `datetime` objects
(UTC unless the API supplies an offset).

## User

`get_user` returns the account that is logged in. `user.id` is a stable
identifier for the account:

    async with SunsynkClient(sunsynk_username, sunsynk_password) as client:
        user = await client.get_user()
        print(f"Logged in as {user.email} (id {user.id})")

## Battery Presence

The API does not say if a battery is connected. `Battery.is_present` returns
`True` when the API reports a battery count or a DC voltage above zero:

    battery = await client.get_inverter_realtime_battery(inverter.sn)
    if battery.is_present:
        print(f"Battery at {battery.soc}%")

## Load, Plant Details and Weather

In addition to the inverter realtime data shown above, the client can also read
the realtime load/UPS metrics, full plant details (including coordinates), and
the weather for a plant's location:

    async with SunsynkClient(sunsynk_username, sunsynk_password) as client:
        inverters = await client.get_inverters()
        load = await client.get_inverter_realtime_load(inverters[0].sn)
        print(f"Load is drawing {load.get_power()}W ({load.daily_used} kWh used today)")

        # get_plant returns the full plant detail, including lon/lat coordinates
        plant = await client.get_plant(inverters[0].plant.id)

        # The Sunsynk weather endpoint expects the coordinates as "lat,lon"
        weather = await client.get_weather(f"{plant.lat},{plant.lon}")
        print(f"It is currently {weather.get_current_temp()}C and {weather.description}")

`get_weather` defaults to today's date; pass `date="YYYY-MM-DD"` to request a
specific day.
