from sunsynk.pviv import PvIv
from sunsynk.resource import Resource


class Input(Resource):
    def __init__(self, data):
        self.generated_today = data['etoday']
        self.generated_total = data['etotal']
        self.pac = data['pac']
        self.pv_iv = [PvIv(pviv_data) for pviv_data in data['pvIV']]

    def get_power(self):
        return sum(float(x.ppv) for x in self.pv_iv)
