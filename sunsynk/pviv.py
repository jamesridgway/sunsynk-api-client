from typing import Any

from sunsynk.resource import Resource, to_datetime, to_float, to_int


class PvIv(Resource):
    """Realtime data for one PV string."""

    def __init__(self, data: dict[str, Any]):
        self.id = data.get('id')
        self.pv_no = to_int(data.get('pvNo'))
        self.vpv = to_float(data.get('vpv'))
        self.ipv = to_float(data.get('ipv'))
        self.ppv = to_float(data.get('ppv'))
        self.today_pv = to_float(data.get('todayPv'))
        self.sn = data.get('sn')
        self.time = to_datetime(data.get('time'))


class MpptIv(Resource):
    """Realtime data for one MPPT tracker."""

    def __init__(self, data: dict[str, Any]):
        self.id = data.get('id')
        self.mppt_no = to_int(data.get('mpptNo', data.get('pvNo')))
        self.vpv = to_float(data.get('vpv'))
        self.ipv = to_float(data.get('ipv'))
        self.ppv = to_float(data.get('ppv'))
        self.today_pv = to_float(data.get('todayPv'))
        self.sn = data.get('sn')
        self.time = to_datetime(data.get('time'))
