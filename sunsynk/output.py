from sunsynk.resource import Resource
from sunsynk.vip import Vip


class Output(Resource):
    def __init__(self, data):
        self.vip = [Vip(vip_data) for vip_data in data['vip']]
        self.p_inv = data['pInv']
        self.pac = data['pac']
        self.fac = data['fac']
