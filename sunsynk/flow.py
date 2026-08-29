from typing import Any

from sunsynk.resource import Resource, to_float, to_int


class Flow(Resource):
    """The energy flow between PV, battery, grid, load and generator for an inverter.

    Returned by ``api/v1/inverter/{sn}/flow``. This is the data behind the
    flow diagram in the Sunsynk Connect app and gives every power value in
    a single request.
    """

    def __init__(self, data: dict[str, Any]):
        self.cust_code = to_int(data.get('custCode'))
        self.protocol_identifier = data.get('protocolIdentifier')
        self.meter_code = to_int(data.get('meterCode'))
        self.pv_power = to_float(data.get('pvPower'))
        self.battery_power = to_float(data.get('battPower'))
        self.battery_power_2 = to_float(data.get('battPower2'))
        self.grid_or_meter_power = to_float(data.get('gridOrMeterPower'))
        self.load_or_eps_power = to_float(data.get('loadOrEpsPower'))
        self.generator_power = to_float(data.get('genPower'))
        self.micro_inverter_power = to_float(data.get('minPower'))
        self.soc = to_float(data.get('soc'))
        self.soc_2 = to_float(data.get('soc2'))
        self.heat_pump_power = to_float(data.get('heatPumpPower'))
        self.smart_load_power = to_float(data.get('smartLoadPower'))
        self.ups_load_power = to_float(data.get('upsLoadPower'))
        self.home_load_power = to_float(data.get('homeLoadPower'))
        # Status flags describing which arrows are active in the flow diagram
        self.pv_to = data.get('pvTo')
        self.to_load = data.get('toLoad')
        self.to_grid = data.get('toGrid')
        self.to_bat = data.get('toBat')
        self.bat_to = data.get('batTo')
        self.grid_to = data.get('gridTo')
        self.gen_to = data.get('genTo')
        self.min_to = data.get('minTo')
        self.exists_gen = data.get('existsGen')
        self.exists_min = data.get('existsMin')
        self.gen_on = data.get('genOn')
        self.micro_on = data.get('microOn')
        self.exists_meter = data.get('existsMeter')
        self.bms_comm_fault_flag = data.get('bmsCommFaultFlag')
        self.exist_think_power = data.get('existThinkPower')
        self.raw = data
