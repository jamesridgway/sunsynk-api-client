from typing import Any

from sunsynk.resource import Resource, to_bool, to_float, to_int


class Settings(Resource):
    """Inverter settings, as returned by ``api/v1/common/setting/{sn}/read``.

    The settings endpoint returns several hundred fields, almost all of them
    as strings. The most commonly used settings are exposed as typed
    attributes; everything is available in ``raw`` and via ``get()``.

    To change settings, modify ``raw`` (or build a smaller dict of just the
    keys to change) and pass it to ``SunsynkClient.set_inverter_settings``.
    """

    TIMER_SLOTS = 6

    def __init__(self, data: dict[str, Any]):
        self.raw: dict[str, Any] = dict(data)
        self.sn = data.get('sn')
        # 0 = battery first, 1 = load first
        self.energy_mode = to_int(data.get('energyMode'))
        # 1 = limited to load (essential only), 2 = limited to home, 3 = zero export
        self.sys_work_mode = to_int(data.get('sysWorkMode'))
        self.work_state = data.get('workState')
        self.battery_low_cap = to_int(data.get('batteryLowCap'))
        self.battery_shutdown_cap = to_int(data.get('batteryShutdownCap'))
        self.battery_restart_cap = to_int(data.get('batteryRestartCap'))
        self.battery_cap = to_float(data.get('batteryCap'))
        self.battery_max_current_charge = to_float(data.get('batteryMaxCurrentCharge'))
        self.battery_max_current_discharge = to_float(data.get('batteryMaxCurrentDischarge'))
        self.zero_export_power = to_int(data.get('zeroExportPower'))
        self.solar_sell = to_bool(data.get('solarSell'))
        self.solar_max_sell_power = to_int(data.get('solarMaxSellPower'))
        self.peak_and_valley = to_bool(data.get('peakAndVallery'))
        self.gen_charge_on = to_bool(data.get('genChargeOn'))
        self.grid_peak_shaving = to_bool(data.get('gridPeakShaving'))
        self.grid_peak_power = to_float(data.get('gridPeakPower'))
        self.battery_type = data.get('battType')
        self.lithium_mode = data.get('lithiumMode')
        self.safety_type = data.get('safetyType')
        self.inverter_type = data.get('inverterType')

        # The six "System Mode" timer slots
        self.sell_times = [data.get(f'sellTime{i}') for i in self._slots()]
        self.sell_time_power = [to_int(data.get(f'sellTime{i}Pac')) for i in self._slots()]
        self.sell_time_voltage = [to_float(data.get(f'sellTime{i}Volt')) for i in self._slots()]
        self.capacities = [to_int(data.get(f'cap{i}')) for i in self._slots()]
        self.grid_charge_on = [to_bool(data.get(f'time{i}on')) for i in self._slots()]
        self.gen_time_on = [to_bool(data.get(f'genTime{i}on')) for i in self._slots()]

        # Days on which the timer slots apply
        self.days_on = {
            day: to_bool(data.get(f'{day}On'))
            for day in ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
        }

    @classmethod
    def _slots(cls) -> range:
        return range(1, cls.TIMER_SLOTS + 1)

    def get(self, key: str, default: Any = None) -> Any:
        """Return a raw setting by its API name."""
        return self.raw.get(key, default)

    def is_battery_first(self) -> bool | None:
        if self.energy_mode is None:
            return None
        return self.energy_mode == 0

    def is_essential_only(self) -> bool | None:
        if self.sys_work_mode is None:
            return None
        return self.sys_work_mode == 1

    def is_grid_charge_enabled(self) -> bool | None:
        """Return True if any timer slot has grid charge enabled."""
        values = [v for v in self.grid_charge_on if v is not None]
        if not values:
            return None
        return any(values)
