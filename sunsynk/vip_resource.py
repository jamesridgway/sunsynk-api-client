from sunsynk.resource import Resource


class VipResource(Resource):
    vip = []

    def get_voltage(self) -> float | None:
        if len(self.vip) == 0:
            return None
        return float(self.vip[0].voltage)

    def get_current(self) -> float | None:
        if len(self.vip) == 0:
            return None
        return float(self.vip[0].current)

    def get_power(self) -> float | None:
        if len(self.vip) == 0:
            return None
        return float(self.vip[0].power)
