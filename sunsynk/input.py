from typing import Any

from sunsynk.pviv import MpptIv, PvIv
from sunsynk.resource import Resource, to_float


class Input(Resource):
    """Realtime PV input data for an inverter."""

    def __init__(self, data: dict[str, Any]):
        self.generated_today = to_float(data.get('etoday'))
        self.generated_total = to_float(data.get('etotal'))
        self.pac = to_float(data.get('pac'))
        self.grid_tip_power = to_float(data.get('gridTipPower'))
        self.pv_iv = [PvIv(pviv_data) for pviv_data in data.get('pvIV') or []]
        self.mppt_iv = [MpptIv(mppt_data) for mppt_data in data.get('mpptIV') or []]

    def get_power(self) -> float:
        """Return the total PV power across all strings.

        Falls back to the inverter reported ``pac`` when no per-string data
        is available (for example on models that only report ``mpptIV``).
        """
        if self.pv_iv:
            return sum(x.ppv or 0.0 for x in self.pv_iv)
        if self.mppt_iv:
            return sum(x.ppv or 0.0 for x in self.mppt_iv)
        return self.pac or 0.0
