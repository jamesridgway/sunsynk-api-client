from typing import Any

from sunsynk.resource import Resource, to_datetime, to_float, to_int


class InverterVersion(Resource):
    def __init__(self, data: dict[str, Any]):
        self.master_ver = data.get('masterVer')
        self.soft_ver = data.get('softVer')
        self.hard_ver = data.get('hardVer')
        self.hmi_ver = data.get('hmiVer')
        self.bms_ver = data.get('bmsVer')
        self.comm_ver = data.get('commVer')


class PlantSummary(Resource):
    def __init__(self, data: dict[str, Any]):
        self.id = to_int(data.get('id'))
        self.name = data.get('name')
        self.type = to_int(data.get('type'))
        self.master = data.get('master')
        self.installer = data.get('installer')
        self.email = data.get('email')
        self.phone = data.get('phone')


class GatewayInfo(Resource):
    def __init__(self, data: dict[str, Any]):
        self.gsn = data.get('gsn')
        self.status = to_int(data.get('status'))


class InverterUser(Resource):
    """The account an inverter is registered to."""

    def __init__(self, data: dict[str, Any]):
        self.id = to_int(data.get('id'))
        self.nickname = data.get('nickname')
        self.mobile = data.get('mobile')
        self.email = data.get('email')


class Inverter(Resource):
    """An inverter as returned by the inverter list endpoint."""

    def __init__(self, data: dict[str, Any]):
        self.id = to_int(data.get('id'))
        self.sn: str = data.get('sn')
        self.alias = data.get('alias')
        self.gsn = data.get('gsn')
        self.status = to_int(data.get('status'))
        self.type = to_int(data.get('type'))
        self.equip_type = to_int(data.get('equipType'))
        self.comm_type_name = data.get('commTypeName')
        self.cust_code = to_int(data.get('custCode'))
        self.version = InverterVersion(data['version']) if data.get('version') else None
        self.model = data.get('model')
        self.equip_mode = to_int(data.get('equipMode'))
        self.pac = to_float(data.get('pac'))
        self.generated_today = to_float(data.get('etoday'))
        self.generated_total = to_float(data.get('etotal'))
        self.updated_at = to_datetime(data.get('updateAt'))
        self.opened = to_int(data.get('opened'))
        self.plant = PlantSummary(data['plant']) if data.get('plant') else None
        self.gateway = GatewayInfo(data['gatewayVO']) if data.get('gatewayVO') else None
        self.sunsynk_equip = data.get('sunsynkEquip')
        self.protocol_identifier = data.get('protocolIdentifier')


class InverterDetails(Inverter):
    """Full details for one inverter, as returned by ``api/v1/inverter/{sn}``."""

    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
        self.run_status = to_int(data.get('runStatus'))
        self.thumb_url = data.get('thumbUrl')
        self.comm_type = to_int(data.get('commType'))
        self.rate_power = to_float(data.get('ratePower'))
        self.brand = data.get('brand')
        self.address = data.get('address')
        self.generated_month = to_float(data.get('emonth'))
        self.generated_year = to_float(data.get('eyear'))
        self.user = InverterUser(data['user']) if data.get('user') else None
