from typing import Any

from sunsynk.resource import Resource, to_float, to_int


class Battery(Resource):
    """Realtime battery data for an inverter."""

    def __init__(self, data: dict[str, Any]):  # pylint: disable=too-many-statements
        self.time = data.get('time')
        self.charge_today = to_float(data.get('etodayChg'))
        self.discharge_today = to_float(data.get('etodayDischg'))
        self.charge_month = to_float(data.get('emonthChg'))
        self.discharge_month = to_float(data.get('emonthDischg'))
        self.charge_year = to_float(data.get('eyearChg'))
        self.discharge_year = to_float(data.get('eyearDischg'))
        self.charge_total = to_float(data.get('etotalChg'))
        self.discharge_total = to_float(data.get('etotalDischg'))
        self.type = to_int(data.get('type'))
        self.power = to_float(data.get('power'))
        self.capacity = to_float(data.get('capacity'))
        self.correct_cap = to_float(data.get('correctCap'))
        self.current = to_float(data.get('current'))
        self.voltage = to_float(data.get('voltage'))
        self.temp = to_float(data.get('temp'))
        self.soc = to_float(data.get('soc'))
        # Values reported by the battery management system (BMS)
        self.bms_soc = to_float(data.get('bmsSoc'))
        self.bms_voltage = to_float(data.get('bmsVolt'))
        self.bms_current = to_float(data.get('bmsCurrent'))
        self.bms_temp = to_float(data.get('bmsTemp'))
        self.bms_1_version_1 = data.get('bms1Version1')
        self.bms_1_version_2 = data.get('bms1Version2')
        self.bms_2_version_1 = data.get('bms2Version1')
        self.bms_2_version_2 = data.get('bms2Version2')
        self.charge_voltage = to_float(data.get('chargeVolt'))
        self.discharge_voltage = to_float(data.get('dischargeVolt'))
        self.charge_current_limit = to_float(data.get('chargeCurrentLimit'))
        self.discharge_current_limit = to_float(data.get('dischargeCurrentLimit'))
        self.max_charge_current_limit = to_float(data.get('maxChargeCurrentLimit'))
        self.max_discharge_current_limit = to_float(data.get('maxDischargeCurrentLimit'))
        # Second battery bank (dual battery systems)
        self.current_2 = to_float(data.get('current2'))
        self.voltage_2 = to_float(data.get('voltage2'))
        self.temp_2 = to_float(data.get('temp2'))
        self.soc_2 = to_float(data.get('soc2'))
        self.charge_voltage_2 = to_float(data.get('chargeVolt2'))
        self.discharge_voltage_2 = to_float(data.get('dischargeVolt2'))
        self.charge_current_limit_2 = to_float(data.get('chargeCurrentLimit2'))
        self.discharge_current_limit_2 = to_float(data.get('dischargeCurrentLimit2'))
        self.max_charge_current_limit_2 = to_float(data.get('maxChargeCurrentLimit2'))
        self.max_discharge_current_limit_2 = to_float(data.get('maxDischargeCurrentLimit2'))
        self.status = to_int(data.get('status'))
        self.battery_soc_1 = to_float(data.get('batterySoc1'))
        self.battery_current_1 = to_float(data.get('batteryCurrent1'))
        self.battery_volt_1 = to_float(data.get('batteryVolt1'))
        self.battery_power_1 = to_float(data.get('batteryPower1'))
        self.battery_temp_1 = to_float(data.get('batteryTemp1'))
        self.battery_status_2 = to_int(data.get('batteryStatus2'))
        self.battery_soc_2 = to_float(data.get('batterySoc2'))
        self.battery_current_2 = to_float(data.get('batteryCurrent2'))
        self.battery_volt_2 = to_float(data.get('batteryVolt2'))
        self.battery_power_2 = to_float(data.get('batteryPower2'))
        self.battery_temp_2 = to_float(data.get('batteryTemp2'))
        self.number_of_batteries = to_int(data.get('numberOfBatteries'))
        self.batt_1_factory = data.get('batt1Factory')
        self.batt_2_factory = data.get('batt2Factory')

    def get_voltage(self) -> float | None:
        return self.voltage

    def get_current(self) -> float | None:
        return self.current

    def get_power(self) -> float | None:
        return self.power

    def get_soc(self) -> float | None:
        """Return the state of charge, preferring the BMS reported value."""
        return self.bms_soc if self.bms_soc is not None else self.soc
