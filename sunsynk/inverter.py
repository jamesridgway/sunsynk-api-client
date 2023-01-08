import datetime

from sunsynk.resource import Resource


class InverterVersion(Resource):
    def __init__(self, data):
        self.master_ver = data.get('masterVer')
        self.soft_ver = data.get('softVer')
        self.hard_ver = data.get('hardVer')
        self.hmi_ver = data.get('hmiVer')
        self.bms_ver = data.get('bmsVer')


class PlantSummary(Resource):
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.type = data.get('type')
        self.master = data.get('master')
        self.installer = data.get('installer')
        self.email = data.get('email')
        self.phone = data.get('phone')


class GatewayInfo(Resource):
    def __init__(self, data):
        self.gsn = data.get('gsn')
        self.status = data.get('status')


class Inverter(Resource):
    def __init__(self, data):
        self.sn = data.get('sn')
        self.alias = data.get('alias')
        self.gsn = data.get('gsn')
        self.status = data.get('status')
        self.type = data.get('type')
        self.comm_type_name = data.get('commTypeName')
        self.cust_code = data.get('custCode')
        self.version = InverterVersion(data.get('version')) if 'version' in data.keys() else None
        self.model = data.get('model')
        self.equip_mode = data.get('equipMode')
        self.pac = data.get('pac')
        self.generated_today = data.get('etoday')
        self.generated_total = data.get('etotal')
        self.updated_at = datetime.datetime\
            .strptime(data.get('updateAt'), "%Y-%m-%dT%H:%M:%SZ") if 'updateAt' in data.keys() else None
        self.opened = data.get('opened')
        self.plant = PlantSummary(data.get('plant')) if 'plant' in data.keys() else None
        self.gateway = GatewayInfo(data.get('gatewayVO')) if 'gatewayVO' in data.keys() else None
        self.sunsynk_equip = data.get('sunsynkEquip')
        self.protocol_identifier = data.get('protocolIdentifier')
