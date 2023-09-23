from sunsynk.resource import Resource


class Battery(Resource):
    def __init__(self, data):
        self.charge_today = data['etodayChg']
        self.discharge_today = data['etodayDischg']
        self.charge_month = data['emonthChg']
        self.discharge_month = data['emonthDischg']
        self.charge_year = data['eyearChg']
        self.discharge_year = data['eyearDischg']
        self.charge_total = data['etotalChg']
        self.discharge_total = data['etotalDischg']
        self.type = data['type']
        self.power = data['power']
        self.capacity = data['capacity']
        self.correct_cap = data['correctCap']
        self.current = data['current']
        self.voltage = data['voltage']
        self.temp = data['temp']
        self.soc = data['soc']
        self.charge_voltage = data['chargeVolt']
        self.discharge_voltage = data['dischargeVolt']
        self.charge_current_limit = data['chargeCurrentLimit']
        self.discharge_current_limit = data['dischargeCurrentLimit']
        self.max_charge_current_limit = data['maxChargeCurrentLimit']
        self.max_discharge_current_limit = data['maxDischargeCurrentLimit']
        self.status = data['status']
        self.battery_soc_1 = data['batterySoc1']
        self.battery_current_1 = data['batteryCurrent1']
        self.battery_volt_1 = data['batteryVolt1']
        self.battery_power_1 = data['batteryPower1']
        self.battery_temp_1 = data['batteryTemp1']
        self.battery_status_2 = data['batteryStatus2']
        self.battery_soc_2 = data['batterySoc2']
        self.battery_current_2 = data['batteryCurrent2']
        self.battery_volt_2 = data['batteryVolt2']
        self.battery_power_2 = data['batteryPower2']
        self.battery_temp_2 = data['batteryTemp2']
        self.number_of_batteries = data['numberOfBatteries']
        self.batt_1_factory = data['batt1Factory']
        self.batt_2_factory = data['batt2Factory']

    def get_voltage(self) -> float:
        return float(self.voltage)

    def get_current(self) -> float:
        return float(self.current)

    def get_power(self) -> float:
        return float(self.power)
