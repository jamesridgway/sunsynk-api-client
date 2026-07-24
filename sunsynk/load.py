from sunsynk.vip import Vip
from sunsynk.vip_resource import VipResource


class Load(VipResource):
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
