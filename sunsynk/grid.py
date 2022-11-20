from sunsynk.resource import Resource
from sunsynk.vip import Vip


class Grid(Resource):
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

    def get_voltage(self):
        if len(self.vip) == 0:
            return None
        return self.vip[0].voltage

    def get_current(self):
        if len(self.vip) == 0:
            return None
        return self.vip[0].current

    def get_power(self):
        if len(self.vip) == 0:
            return None
        return self.vip[0].power
