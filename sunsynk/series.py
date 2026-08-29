from typing import Any

from sunsynk.resource import Resource, to_datetime, to_float


class Record(Resource):
    """One sample in a time series."""

    def __init__(self, data: dict[str, Any]):
        self.time = data.get('time')
        self.timestamp = to_datetime(data.get('time'))
        self.value = to_float(data.get('value'))
        self.updated_at = to_datetime(data.get('updateTime'))


class Series(Resource):
    """One column of a time series response, for example ``dc_temp``."""

    def __init__(self, data: dict[str, Any]):
        self.label = data.get('label')
        self.unit = data.get('unit')
        self.records = [Record(record) for record in data.get('records') or []]

    def latest(self) -> Record | None:
        """Return the most recent sample, or None if there are no samples."""
        if not self.records:
            return None
        return self.records[-1]

    def latest_value(self) -> float | None:
        latest = self.latest()
        return latest.value if latest else None


class SeriesData(Resource):
    """A response containing one or more time series (``infos``).

    Used by the inverter ``output/day`` endpoint and the plant ``energy``
    endpoints.
    """

    def __init__(self, data: dict[str, Any]):
        self.series = [Series(info) for info in data.get('infos') or []]

    def get_series(self, label: str) -> Series | None:
        """Return the series whose label matches (case-insensitive), or None."""
        wanted = label.lower().replace('_', ' ').strip()
        for series in self.series:
            if (series.label or '').lower().replace('_', ' ').strip() == wanted:
                return series
        return None

    def find_series(self, *keywords: str) -> Series | None:
        """Return the first series whose label contains all of the keywords (case-insensitive)."""
        lowered = [k.lower() for k in keywords]
        for series in self.series:
            label = (series.label or '').lower()
            if all(k in label for k in lowered):
                return series
        return None


class InverterTemperatures(SeriesData):
    """DC and IGBT (AC) temperature history for an inverter for one day."""

    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
        self.dc_temp = self.find_series('dc') or (self.series[0] if len(self.series) > 0 else None)
        self.igbt_temp = self.find_series('igbt') or self.find_series('ac') or (
            self.series[1] if len(self.series) > 1 else None)

    def get_dc_temp(self) -> float | None:
        return self.dc_temp.latest_value() if self.dc_temp else None

    def get_igbt_temp(self) -> float | None:
        return self.igbt_temp.latest_value() if self.igbt_temp else None
