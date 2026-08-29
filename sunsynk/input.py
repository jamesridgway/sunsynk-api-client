from typing import Any

from sunsynk.pviv import PvIv
from sunsynk.resource import Resource, to_float


class Input(Resource):
    """Realtime PV input data for an inverter."""

    def __init__(self, data: dict[str, Any]):
        self.generated_today = to_float(data.get('etoday'))
        self.generated_total = to_float(data.get('etotal'))
        self.pac = to_float(data.get('pac'))
        self.pv_iv = [PvIv(pviv_data) for pviv_data in data.get('pvIV') or []]

    def get_power(self) -> float:
        """Return the total PV power across all strings."""
        return sum(x.ppv or 0.0 for x in self.pv_iv)
