import datetime

from sunsynk.resource import Resource


class InverterVersion(Resource):
    def __init__(self, data):
        self.master_ver = data['masterVer']
        self.soft_ver = data['softVer']
        self.hard_ver = data['hardVer']
        self.hmi_ver = data['hmiVer']
        self.bms_ver = data['bmsVer']


class PlantSummary(Resource):
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.type = data['type']
        self.master = data['master']
        self.installer = data['installer']
        self.email = data['email']
        self.phone = data['phone']


class GatewayInfo(Resource):
    def __init__(self, data):
        self.gsn = data['gsn']
        self.status = data['status']


class Inverter(Resource):
    def __init__(self, data):
        self.sn = data['sn']
        self.alias = data['alias']
        self.gsn = data['gsn']
        self.status = data['status']
        self.type = data['type']
        self.comm_type_name = data['commTypeName']
        self.cust_code = data['custCode']
        self.version = InverterVersion(data['version'])
        self.model = data['model']
        self.equip_mode = data['equipMode']
        self.pac = data['pac']
        self.generated_today = data['etoday']
        self.generated_total = data['etotal']
        self.updated_at = datetime.datetime.strptime(data['updateAt'], "%Y-%m-%dT%H:%M:%SZ")
        self.opened = data['opened']
        self.plant = PlantSummary(data['plant'])
        self.gateway = GatewayInfo(data['gatewayVO'])
        self.sunsynk_equip = data['sunsynkEquip']
        self.protocol_identifier = data['protocolIdentifier']
