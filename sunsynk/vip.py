from typing import Any

from sunsynk.resource import Resource, to_float


class Vip(Resource):
    """Voltage, current and power for one phase."""

    def __init__(self, data: dict[str, Any]):
        self.voltage = to_float(data.get('volt'))
        self.current = to_float(data.get('current'))
        self.power = to_float(data.get('power'))
