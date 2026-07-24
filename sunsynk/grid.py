from sunsynk.vip import Vip
from sunsynk.vip_resource import VipResource


class Grid(VipResource):
    def __init__(self, data):
        self.vip = [Vip(vip_data) for vip_data in data['vip']]
        self.pac = data['pac']
        self.qac = data['qac']
        self.fac = data['fac']
        self.fac = data['fac']
        self.pf = data['pf']
        self.status = data['status']
        self.today_import = data['etodayFrom']
        self.today_export = data['etodayTo']
        self.total_import = data['etotalFrom']
        self.total_export = data['etotalTo']
        self.limiter_power_arr = data['limiterPowerArr']
        self.limiter_total_power = data['limiterTotalPower']
