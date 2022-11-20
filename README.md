# Sunsynk API Client
[![CI](https://github.com/jamesridgway/sunsynk-api-client/actions/workflows/ci.yml/badge.svg)](https://github.com/jamesridgway/sunsynk-api-client/actions/workflows/ci.yml)

An API client library for reading data from the Sunsynk API that is used by the Sunsynk Connect apps and 
[PowerView](https://pv.inteless.com/) portal.


## Example Usage

    import os
    
    from sunsynk.client import SunsynkClient
    
    sunsynk_username = os.getenv('SUNSYNK_USERNAME')
    sunsynk_password = os.getenv('SUNSYNK_PASSWORD')
    
    client = SunsynkClient(sunsynk_username, sunsynk_password)
    
    inverters = client.get_inverters()
    for inverter in inverters:
        grid = client.get_inverter_realtime_grid(inverter.sn)
        battery = client.get_inverter_realtime_battery(inverter.sn)
        solar_pv = client.get_inverter_realtime_input(inverter.sn)
    
        print(f"Inverter (sn: {inverter.sn}) is drawing {grid.get_power()}kWh from the grid, {battery.power}kWh from battery and {solar_pv.get_power()}kWh.")

