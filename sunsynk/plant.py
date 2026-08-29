from typing import Any

from sunsynk.resource import Resource, to_datetime, to_float, to_int


class Currency(Resource):
    def __init__(self, data: dict[str, Any]):
        self.id = to_int(data.get('id'))
        self.code = data.get('code')
        self.text = data.get('text')


class Plant(Resource):
    """A plant, as returned by the plant list and plant detail endpoints."""

    def __init__(self, data: dict[str, Any]):
        self.id = to_int(data.get('id'))
        self.name = data.get('name')
        self.thumb_url = data.get('thumbUrl')
        self.status = to_int(data.get('status'))
        self.address = data.get('address')

        realtime = data.get('realtime') or {}
        self.pac = to_float(data.get('pac') if 'pac' in data else realtime.get('pac'))
        self.efficiency = to_float(data.get('efficiency') if 'efficiency' in data else realtime.get('efficiency'))
        self.generation_today = to_float(data.get('etoday') if 'etoday' in data else realtime.get('etoday'))
        self.generation_month = to_float(data.get('emonth') if 'emonth' in data else realtime.get('emonth'))
        self.generation_year = to_float(data.get('eyear') if 'eyear' in data else realtime.get('eyear'))
        self.generation_total = to_float(data.get('etotal') if 'etotal' in data else realtime.get('etotal'))
        self.total_power = to_float(data.get('totalPower') if 'totalPower' in data else realtime.get('totalPower'))
        self.income = to_float(data.get('income') if 'income' in data else realtime.get('income'))
        self.invest = to_float(data.get('invest'))
        self.currency = Currency(data['currency']) if data.get('currency') else None

        self.updated_at = to_datetime(data.get('updateAt') or realtime.get('updateAt'))
        self.created_at = to_datetime(data.get('createAt'))

        self.type = to_int(data.get('type'))

        if 'masterId' in data:
            self.master_id = to_int(data['masterId'])
        elif data.get('master'):
            self.master_id = to_int(data['master'].get('id'))
        else:
            self.master_id = None

        self.share = data.get('share')
        self.plant_permissions = data.get('plantPermission')
        self.exist_camera = data.get('existCamera')

        self.lon = to_float(data.get('lon'))
        self.lat = to_float(data.get('lat'))


class PlantRealtime(Resource):
    """Realtime totals for a plant, as returned by ``api/v1/plant/{id}/realtime``."""

    def __init__(self, data: dict[str, Any]):
        self.pac = to_float(data.get('pac'))
        self.efficiency = to_float(data.get('efficiency'))
        self.generation_today = to_float(data.get('etoday'))
        self.generation_month = to_float(data.get('emonth'))
        self.generation_year = to_float(data.get('eyear'))
        self.generation_total = to_float(data.get('etotal'))
        self.total_power = to_float(data.get('totalPower'))
        self.invest = to_float(data.get('invest'))
        self.income = to_float(data.get('income'))
        self.currency = Currency(data['currency']) if data.get('currency') else None
        self.updated_at = to_datetime(data.get('updateAt'))
