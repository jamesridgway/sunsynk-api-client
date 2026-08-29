from typing import Any

from sunsynk.resource import to_float, to_int
from sunsynk.vip import Vip
from sunsynk.vip_resource import VipResource


class Load(VipResource):
    """Realtime load data for an inverter."""

    def __init__(self, data: dict[str, Any]):
        self.total_used = to_float(data.get('totalUsed'))
        self.daily_used = to_float(data.get('dailyUsed'))
        self.vip = [Vip(vip_data) for vip_data in data.get('vip') or []]
        self.total_power = to_float(data.get('totalPower'))
        self.smart_load_status = to_int(data.get('smartLoadStatus'))
        self.load_fac = to_float(data.get('loadFac'))
        self.ups_power_l1 = to_float(data.get('upsPowerL1'))
        self.ups_power_l2 = to_float(data.get('upsPowerL2'))
        self.ups_power_l3 = to_float(data.get('upsPowerL3'))
        self.ups_power_total = to_float(data.get('upsPowerTotal'))

    def get_total_power(self) -> float | None:
        """Return the total load power across all phases."""
        return self.total_power
