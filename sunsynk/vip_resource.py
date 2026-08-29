from sunsynk.resource import Resource
from sunsynk.vip import Vip


class VipResource(Resource):
    vip: list[Vip] = []

    def get_voltage(self) -> float | None:
        """Return the voltage of the first phase."""
        if len(self.vip) == 0:
            return None
        return self.vip[0].voltage

    def get_current(self) -> float | None:
        """Return the current of the first phase."""
        if len(self.vip) == 0:
            return None
        return self.vip[0].current

    def get_power(self) -> float | None:
        """Return the power of the first phase."""
        if len(self.vip) == 0:
            return None
        return self.vip[0].power
