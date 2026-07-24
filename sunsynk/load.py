from sunsynk.resource import Resource
from sunsynk.vip import Vip


class Load(Resource):
    def __init__(self, data):
        self.total_used = data['totalUsed']
        self.daily_used = data['dailyUsed']
        self.vip = [Vip(vip_data) for vip_data in data.get('vip', [])]
        self.total_power = data['totalPower']
        self.smart_load_status = data['smartLoadStatus']
        self.load_fac = data['loadFac']
        self.ups_power_l1 = data['upsPowerL1']
        self.ups_power_l2 = data['upsPowerL2']
        self.ups_power_l3 = data['upsPowerL3']
        self.ups_power_total = data['upsPowerTotal']

    def get_voltage(self) -> float | None:
        if len(self.vip) == 0:
            return None
        return float(self.vip[0].voltage)

    def get_current(self) -> float | None:
        if len(self.vip) == 0:
            return None
        return float(self.vip[0].current)

    def get_power(self) -> float | None:
        if len(self.vip) == 0:
            return None
        return float(self.vip[0].power)
