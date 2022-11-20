import datetime

from sunsynk.resource import Resource


class PvIv(Resource):
    def __init__(self, data):
        self.id = data['id']
        self.pv_no = data['pvNo']
        self.vpv = data['vpv']
        self.ipv = data['ipv']
        self.ppv = data['ppv']
        self.today_pv = data['todayPv']
        self.sn = data['sn']
        self.time = datetime.datetime.strptime(data['time'], "%Y-%m-%d %H:%M:%S")
