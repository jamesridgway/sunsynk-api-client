# Sunsynk API Client
[![CI](https://github.com/jamesridgway/sunsynk-api-client/actions/workflows/ci.yml/badge.svg)](https://github.com/jamesridgway/sunsynk-api-client/actions/workflows/ci.yml)

An API client library for reading data from the Sunsynk API that is used by the Sunsynk Connect apps and 
[PowerView](https://pv.inteless.com/) portal.


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
    
                print(f"Inverter (sn: {inverter.sn}) is drawing {grid.get_power()}W from the grid, {battery.power}W from battery and {solar_pv.get_power()}W.")
    
        print('Done!')
    
    asyncio.run(main())


## Use With an Existing aiohttp Session

Pass a `session` to share an existing `aiohttp.ClientSession`. The client does
not close a shared session:

    async with aiohttp.ClientSession() as session:
        client = SunsynkClient(sunsynk_username, sunsynk_password, session=session)
        await client.login()
        inverters = await client.get_inverters()

## Errors

All errors raised by the client subclass `sunsynk.exceptions.SunsynkError`:

* `SunsynkAuthenticationError` - the username or password is not correct.
* `SunsynkConnectionError` - the API could not be reached, timed out, or
  returned an unexpected response.

Numeric values in the API responses are converted to `float` or `int`. Values
that are missing are `None`.

## User

`get_user` returns the account that is logged in. `user.id` is a stable
identifier for the account:

    async with SunsynkClient(sunsynk_username, sunsynk_password) as client:
        user = await client.get_user()
        print(f"Logged in as {user.email} (id {user.id})")

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
