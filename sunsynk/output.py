from typing import Any

from sunsynk.resource import to_float
from sunsynk.vip import Vip
from sunsynk.vip_resource import VipResource


class Output(VipResource):
    """Realtime output data for an inverter."""

    def __init__(self, data: dict[str, Any]):
        self.vip = [Vip(vip_data) for vip_data in data.get('vip') or []]
        self.p_inv = to_float(data.get('pInv'))
        self.pac = to_float(data.get('pac'))
        self.fac = to_float(data.get('fac'))
