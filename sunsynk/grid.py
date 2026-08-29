from typing import Any

from sunsynk.resource import to_float, to_int
from sunsynk.vip import Vip
from sunsynk.vip_resource import VipResource


class Grid(VipResource):
    """Realtime grid data for an inverter."""

    def __init__(self, data: dict[str, Any]):
        self.vip = [Vip(vip_data) for vip_data in data.get('vip') or []]
        self.power = to_float(data.get('power'))
        self.voltage = to_float(data.get('voltage'))
        self.current = to_float(data.get('current'))
        self.pac = to_float(data.get('pac'))
        self.qac = to_float(data.get('qac'))
        self.fac = to_float(data.get('fac'))
        self.pf = to_float(data.get('pf'))
        self.status = to_int(data.get('status'))
        # The API misspells this as "acRealyStatus"; 1 means the grid relay is closed (grid connected)
        self.ac_relay_status = to_int(data.get('acRealyStatus', data.get('acRelayStatus')))
        self.today_import = to_float(data.get('etodayFrom'))
        self.today_export = to_float(data.get('etodayTo'))
        self.total_import = to_float(data.get('etotalFrom'))
        self.total_export = to_float(data.get('etotalTo'))
        self.limiter_power_arr = data.get('limiterPowerArr')
        self.limiter_total_power = to_float(data.get('limiterTotalPower'))

    def get_total_power(self) -> float | None:
        """Return the total grid power across all phases."""
        return self.pac

    def is_connected(self) -> bool | None:
        """Return True if the grid relay is closed (grid available), None if unknown."""
        if self.ac_relay_status is None:
            return None
        return self.ac_relay_status == 1
