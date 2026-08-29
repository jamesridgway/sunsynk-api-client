import datetime
from typing import Any

from sunsynk.resource import Resource, to_float, to_int


class InverterVersion(Resource):
    def __init__(self, data: dict[str, Any]):
        self.master_ver = data.get('masterVer')
        self.soft_ver = data.get('softVer')
        self.hard_ver = data.get('hardVer')
        self.hmi_ver = data.get('hmiVer')
        self.bms_ver = data.get('bmsVer')


class PlantSummary(Resource):
    def __init__(self, data: dict[str, Any]):
        self.id = data.get('id')
        self.name = data.get('name')
        self.type = data.get('type')
        self.master = data.get('master')
        self.installer = data.get('installer')
        self.email = data.get('email')
        self.phone = data.get('phone')


class GatewayInfo(Resource):
    def __init__(self, data: dict[str, Any]):
        self.gsn = data.get('gsn')
        self.status = data.get('status')


class Inverter(Resource):
    def __init__(self, data: dict[str, Any]):
        self.sn: str = data.get('sn')
        self.alias = data.get('alias')
        self.gsn = data.get('gsn')
        self.status = to_int(data.get('status'))
        self.type = to_int(data.get('type'))
        self.comm_type_name = data.get('commTypeName')
        self.cust_code = data.get('custCode')
        self.version = InverterVersion(data['version']) if data.get('version') else None
        self.model = data.get('model')
        self.equip_mode = data.get('equipMode')
        self.pac = to_float(data.get('pac'))
        self.generated_today = to_float(data.get('etoday'))
        self.generated_total = to_float(data.get('etotal'))
        updated_at = data.get('updateAt')
        self.updated_at = datetime.datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ") if updated_at else None
        self.opened = data.get('opened')
        self.plant = PlantSummary(data['plant']) if data.get('plant') else None
        self.gateway = GatewayInfo(data['gatewayVO']) if data.get('gatewayVO') else None
        self.sunsynk_equip = data.get('sunsynkEquip')
        self.protocol_identifier = data.get('protocolIdentifier')
